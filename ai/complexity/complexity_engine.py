import joblib
import re


# --------------------------------------------------
# Paths
# --------------------------------------------------

MODEL_PATH = "ai/models/complaint_complexity_model.pkl"
VECTORIZER_PATH = "ai/models/complexity_tfidf_vectorizer.pkl"


# --------------------------------------------------
# Load ML Model
# --------------------------------------------------

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


# --------------------------------------------------
# Rule Indicators
# --------------------------------------------------

HIGH_INDICATORS = [
    "completely unavailable",
    "entire platform is down",
    "entire service is down",
    "service outage",
    "system outage",
    "multiple users",
    "repeatedly failing",
    "repeatedly failed",
    "major issue",
    "blocking my work",
    "cannot access",
    "cannot use",
    "crashes",
    "critical",
]

MEDIUM_INDICATORS = [
    "delayed",
    "incorrect",
    "needs to be corrected",
    "problem",
    "issue",
    "not working properly",
    "needs correction",
    "payment issue",
]

LOW_INDICATORS = [
    "simple question",
    "general information",
    "general guidance",
    "guidance",
    "minor issue",
    "basic request",
    "information about",
]


# --------------------------------------------------
# Text Cleaning
# --------------------------------------------------

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# --------------------------------------------------
# Rule-Based Complexity
# --------------------------------------------------

def get_rule_prediction(text):

    text = clean_text(text)

    high_score = 0
    medium_score = 0
    low_score = 0

    for indicator in HIGH_INDICATORS:
        if indicator in text:
            high_score += 1

    for indicator in MEDIUM_INDICATORS:
        if indicator in text:
            medium_score += 1

    for indicator in LOW_INDICATORS:
        if indicator in text:
            low_score += 1

    scores = {
        "High": high_score,
        "Medium": medium_score,
        "Low": low_score
    }

    max_score = max(scores.values())

    if max_score == 0:
        return None, 0

    rule_prediction = max(
        scores,
        key=scores.get
    )

    return rule_prediction, max_score


# --------------------------------------------------
# Hybrid Complexity Engine
# --------------------------------------------------

def predict_complexity(complaint):

    cleaned = clean_text(complaint)

    # ML prediction
    vector = vectorizer.transform([cleaned])

    ml_prediction = model.predict(vector)[0]

    probabilities = model.predict_proba(vector)[0]

    ml_confidence = max(probabilities)

    # Rule prediction
    rule_prediction, rule_score = get_rule_prediction(
        cleaned
    )

    # --------------------------------------------------
    # Decision Logic
    # --------------------------------------------------

    if rule_prediction == "High" and rule_score >= 2:

        final_prediction = "High"
        decision_method = "Strong High Complexity Override"

    elif rule_prediction == "High" and rule_score >= 1:

        final_prediction = "High"
        decision_method = "High Complexity Rule"

    elif rule_prediction == "Low" and rule_score >= 2:

        final_prediction = "Low"
        decision_method = "Strong Low Complexity Rule"

    elif rule_prediction == "Low" and rule_score >= 1:

        final_prediction = "Low"
        decision_method = "Low Complexity Rule"

    elif rule_prediction == "Medium" and rule_score >= 1:

        final_prediction = "Medium"
        decision_method = "Medium Complexity Rule"

    else:

        final_prediction = ml_prediction
        decision_method = "ML Fallback"

    return {
        "complexity": final_prediction,
        "ml_prediction": ml_prediction,
        "ml_confidence": ml_confidence,
        "rule_prediction": rule_prediction,
        "rule_score": rule_score,
        "decision_method": decision_method
    }


# --------------------------------------------------
# Test Complaints
# --------------------------------------------------

test_complaints = [

    "The entire platform is down and I cannot access any service.",

    "Several important features are failing repeatedly and blocking my work.",

    "I cannot complete my payment because the system keeps rejecting it.",

    "My delivery is taking longer than expected.",

    "I need some information about changing my account details.",

    "The website has a small display issue on my profile page.",

    "Multiple attempts to reset my password have failed.",

    "The service is completely unavailable for all users.",

    "My invoice contains an incorrect amount and needs to be corrected.",

    "I have a simple question about the complaint procedure.",

    "The application crashes whenever I try to submit a request.",

    "My order is slightly delayed but I can still wait.",

    "I cannot access my account and several login attempts are failing.",

    "I need general guidance about using the service.",

    "A major system problem is preventing me from completing my work."
]


# --------------------------------------------------
# Run Tests
# --------------------------------------------------

print("=" * 75)
print("HYBRID COMPLEXITY ENGINE V1")
print("=" * 75)

for complaint in test_complaints:

    result = predict_complexity(complaint)

    print("\nComplaint:", complaint)
    print("Final Complexity :", result["complexity"])
    print("ML Prediction    :", result["ml_prediction"])
    print(
        "ML Confidence    : "
        f"{result['ml_confidence'] * 100:.2f}%"
    )
    print(
        "Rule Prediction  : "
        f"{result['rule_prediction']}"
    )
    print(
        "Rule Score       : "
        f"{result['rule_score']}"
    )
    print(
        "Decision Method  : "
        f"{result['decision_method']}"
    )