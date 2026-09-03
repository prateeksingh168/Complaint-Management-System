import re
import joblib


# --------------------------------------------------
# Paths
# --------------------------------------------------

MODEL_PATH = "ai/models/complaint_priority_model.pkl"
VECTORIZER_PATH = "ai/models/priority_tfidf_vectorizer.pkl"


# --------------------------------------------------
# Load ML Model
# --------------------------------------------------

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


# --------------------------------------------------
# Priority Indicators
# --------------------------------------------------

URGENT_INDICATORS = [
    "urgent",
    "critical",
    "completely unavailable",
    "service outage",
    "entire service is down",
    "cannot use the service",
    "service is completely unavailable",
]

HIGH_INDICATORS = [
    "serious",
    "major issue",
    "repeatedly failing",
    "unable to use",
    "cannot complete my work",
]

MEDIUM_INDICATORS = [
    "delayed",
    "incorrect",
    "problem",
    "issue",
    "not working properly",
]

LOW_INDICATORS = [
    "general information",
    "question",
    "guidance",
]


# --------------------------------------------------
# Text Normalization
# --------------------------------------------------

def normalize_text(text):
    """Normalize complaint text for priority analysis."""

    text = str(text).lower()

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
# Rule-Based Priority Score
# --------------------------------------------------

def calculate_rule_priority(text):
    """
    Calculate priority using urgency indicators.

    Returns:
        priority, score
    """

    text = normalize_text(text)

    urgent_score = sum(
        indicator in text
        for indicator in URGENT_INDICATORS
    )

    high_score = sum(
        indicator in text
        for indicator in HIGH_INDICATORS
    )

    medium_score = sum(
        indicator in text
        for indicator in MEDIUM_INDICATORS
    )

    low_score = sum(
        indicator in text
        for indicator in LOW_INDICATORS
    )

    if urgent_score > 0:
        return "Urgent", urgent_score

    if high_score > 0:
        return "High", high_score

    if medium_score > 0:
        return "Medium", medium_score

    if low_score > 0:
        return "Low", low_score

    return None, 0


# --------------------------------------------------
# ML Prediction
# --------------------------------------------------

def predict_ml_priority(text):
    """Predict priority using trained ML model."""

    cleaned_text = normalize_text(text)

    vector = vectorizer.transform(
        [cleaned_text]
    )

    prediction = model.predict(vector)[0]

    return prediction


# --------------------------------------------------
# Hybrid Priority Prediction
# --------------------------------------------------

def predict_priority(text):
    """
    Hybrid priority prediction.

    Rule-based urgency indicators take precedence
    when a strong urgency signal is detected.
    Otherwise, ML prediction is used.
    """

    rule_priority, rule_score = calculate_rule_priority(
        text
    )

    ml_priority = predict_ml_priority(text)

    if rule_priority is not None:

        return {
            "priority": rule_priority,
            "method": "Rule + ML",
            "rule_score": rule_score,
            "ml_prediction": ml_priority,
        }

    return {
        "priority": ml_priority,
        "method": "ML",
        "rule_score": 0,
        "ml_prediction": ml_priority,
    }


# --------------------------------------------------
# Test Examples
# --------------------------------------------------

if __name__ == "__main__":

    test_complaints = [
        "The entire service is completely unavailable.",
        "This is a critical issue and I need help immediately.",
        "My application is repeatedly failing.",
        "My delivery is delayed.",
        "I have a question about the complaint process.",
        "I need general information about the service.",
        "My payment has an incorrect amount.",
        "The website is not working properly.",
    ]

    print("=" * 60)
    print("HYBRID PRIORITY ENGINE TEST")
    print("=" * 60)

    for complaint in test_complaints:

        result = predict_priority(
            complaint
        )

        print("\nComplaint:", complaint)
        print("Priority :", result["priority"])
        print("Method   :", result["method"])
        print("ML       :", result["ml_prediction"])
        print("Rule Score:", result["rule_score"])