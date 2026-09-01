import joblib
import re


# --------------------------------------------------
# Load ML Model
# --------------------------------------------------

MODEL_PATH = "ai/models/complaint_complexity_model.pkl"
VECTORIZER_PATH = "ai/models/complexity_tfidf_vectorizer.pkl"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


# --------------------------------------------------
# Complexity Indicators
# --------------------------------------------------

HIGH_INDICATORS = [
    # System / service failure
    "completely unavailable",
    "entire platform is down",
    "entire service is down",
    "service outage",
    "system outage",
    "system is down",

    # Severe technical problems
    "major system problem",
    "major system issue",
    "major issue",
    "critical issue",
    "critical problem",
    "application crashes",
    "system crashes",

    # Repeated failures
    "repeatedly failing",
    "repeatedly failed",
    "multiple attempts",
    "multiple login attempts",
    "password reset failed",
    "password reset attempts have failed",

    # Access / blocking
    "cannot access",
    "cannot use",
    "blocking my work",
    "preventing me from completing my work",

    # Payment failures
    "payment keeps rejecting",
    "payment is being rejected",
    "payment rejected",
    "payment failing",
    "cannot complete my payment",
]


MEDIUM_INDICATORS = [
    "delivery delayed",
    "order delayed",
    "slightly delayed",
    "taking longer",
    "longer than expected",
    "incorrect amount",
    "needs to be corrected",
    "needs correction",
    "payment issue",
    "not working properly",
    "problem",
    "issue",
]


LOW_INDICATORS = [
    "simple question",
    "general information",
    "general guidance",
    "guidance",
    "basic request",
    "minor issue",
    "small display issue",
    "minor display issue",
    "simple display issue",
    "small issue",
]


# --------------------------------------------------
# Text Cleaning
# --------------------------------------------------

def clean_text(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# --------------------------------------------------
# Rule Engine
# --------------------------------------------------

def get_rule_prediction(text):

    text = clean_text(text)

    high_matches = [
        indicator
        for indicator in HIGH_INDICATORS
        if indicator in text
    ]

    medium_matches = [
        indicator
        for indicator in MEDIUM_INDICATORS
        if indicator in text
    ]

    low_matches = [
        indicator
        for indicator in LOW_INDICATORS
        if indicator in text
    ]

    # --------------------------------------------------
    # Specific High indicators get highest priority
    # --------------------------------------------------

    if high_matches:

        return (
            "High",
            len(high_matches),
            high_matches
        )

    # --------------------------------------------------
    # Specific Low indicators
    # --------------------------------------------------

    if low_matches:

        return (
            "Low",
            len(low_matches),
            low_matches
        )

    # --------------------------------------------------
    # Medium indicators
    # --------------------------------------------------

    if medium_matches:

        return (
            "Medium",
            len(medium_matches),
            medium_matches
        )

    return None, 0, []


# --------------------------------------------------
# Hybrid Complexity Prediction
# --------------------------------------------------

def predict_complexity(complaint):

    cleaned = clean_text(complaint)

    # --------------------------------------------------
    # ML Prediction
    # --------------------------------------------------

    vector = vectorizer.transform(
        [cleaned]
    )

    ml_prediction = model.predict(
        vector
    )[0]

    probabilities = model.predict_proba(
        vector
    )[0]

    ml_confidence = max(
        probabilities
    )

    # --------------------------------------------------
    # Rule Prediction
    # --------------------------------------------------

    rule_prediction, rule_score, matched_rules = (
        get_rule_prediction(cleaned)
    )

    # --------------------------------------------------
    # Final Decision
    # --------------------------------------------------

    if rule_prediction == "High":

        final_prediction = "High"

        decision_method = (
            "High Complexity Rule Override"
        )

    elif rule_prediction == "Low":

        final_prediction = "Low"

        decision_method = (
            "Low Complexity Rule Override"
        )

    elif rule_prediction == "Medium":

        final_prediction = "Medium"

        decision_method = (
            "Medium Complexity Rule"
        )

    else:

        final_prediction = ml_prediction

        decision_method = "ML Fallback"

    return {
        "complexity": final_prediction,
        "ml_prediction": ml_prediction,
        "ml_confidence": ml_confidence,
        "rule_prediction": rule_prediction,
        "rule_score": rule_score,
        "matched_rules": matched_rules,
        "decision_method": decision_method
    }


# --------------------------------------------------
# 15 Test Complaints
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
# Run V2 Test
# --------------------------------------------------

print("=" * 75)
print("HYBRID COMPLEXITY ENGINE V2")
print("=" * 75)


for complaint in test_complaints:

    result = predict_complexity(
        complaint
    )

    print("\nComplaint:", complaint)

    print(
        "Final Complexity :",
        result["complexity"]
    )

    print(
        "ML Prediction    :",
        result["ml_prediction"]
    )

    print(
        "ML Confidence    : "
        f"{result['ml_confidence'] * 100:.2f}%"
    )

    print(
        "Rule Prediction  :",
        result["rule_prediction"]
    )

    print(
        "Rule Score       :",
        result["rule_score"]
    )

    print(
        "Matched Rules    :",
        result["matched_rules"]
    )

    print(
        "Decision Method  :",
        result["decision_method"]
    )