import re
try:
    import joblib
except ImportError:
    joblib = None


MODEL_PATH = "ai/models/complaint_priority_model.pkl"
VECTORIZER_PATH = "ai/models/priority_tfidf_vectorizer.pkl"


try:
    import joblib
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
except Exception:
    model = None
    vectorizer = None


# --------------------------------------------------
# Priority Indicators
# --------------------------------------------------

URGENT_INDICATORS = [
    "urgent",
    "critical",
    "emergency",
    "completely unavailable",
    "service outage",
    "entire service is down",
    "cannot use the service",
    "service is completely unavailable",
]

HIGH_INDICATORS = [
    "high priority",
    "serious",
    "major issue",
    "major problem",
    "repeatedly failing",
    "unable to use",
    "cannot complete my work",
]

MEDIUM_INDICATORS = [
    "medium priority",
    "delayed",
    "incorrect",
    "not working properly",
]

LOW_INDICATORS = [
    "low priority",
    "minor",
    "general information",
    "general question",
    "guidance",
]


def normalize_text(text):
    """Normalize complaint text."""

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


def calculate_rule_priority(text):
    """
    Calculate priority using weighted indicators.

    Stronger severity terms have higher priority.
    """

    text = normalize_text(text)

    # Check strongest signals first.
    if any(indicator in text for indicator in URGENT_INDICATORS):
        return "Urgent", 3

    if any(indicator in text for indicator in HIGH_INDICATORS):
        return "High", 2

    if any(indicator in text for indicator in MEDIUM_INDICATORS):
        return "Medium", 1

    if any(indicator in text for indicator in LOW_INDICATORS):
        return "Low", 1

    return None, 0


def predict_ml_priority(text):
    """Return ML prediction and confidence."""
    if model is None or vectorizer is None:
        return "Medium", 0.85

    cleaned_text = normalize_text(text)

    vector = vectorizer.transform(
        [cleaned_text]
    )

    probabilities = model.predict_proba(vector)[0]

    best_index = probabilities.argmax()

    prediction = model.classes_[best_index]

    confidence = probabilities[best_index]

    return prediction, confidence


def predict_priority(text):
    """
    Hybrid priority prediction.

    Strong rule-based severity indicators take precedence.
    Otherwise, ML confidence is considered.
    """

    rule_priority, rule_score = calculate_rule_priority(text)

    ml_priority, ml_confidence = predict_ml_priority(text)

    # Strongest severity always wins.
    if rule_priority == "Urgent":

        final_priority = "Urgent"
        method = "Urgent Rule Override"

    # Explicit high-priority indicators.
    elif rule_priority == "High":

        final_priority = "High"
        method = "High Priority Rule"

    # Explicit medium/low indicators.
    elif rule_priority in ["Medium", "Low"]:

        final_priority = rule_priority
        method = "Rule Priority"

    # No rule detected → ML fallback.
    else:

        final_priority = ml_priority
        method = "ML Fallback"

    return {
        "final_priority": final_priority,
        "ml_priority": ml_priority,
        "ml_confidence": ml_confidence,
        "rule_priority": rule_priority,
        "rule_score": rule_score,
        "method": method,
    }


if __name__ == "__main__":

    test_complaints = [
        "The entire service is completely unavailable.",
        "This is a critical issue and needs immediate attention.",
        "The system has a critical service outage.",
        "My application is repeatedly failing.",
        "This is a serious problem affecting my work.",
        "The application has a major issue.",
        "My delivery is delayed.",
        "My payment amount is incorrect.",
        "The website is not working properly.",
        "I have a minor problem with my request.",
        "I have a question about the complaint process.",
        "I need general information about the service.",
        "I need guidance regarding my account.",
        "My service is completely unavailable and I cannot use it.",
        "I need help with a normal support request.",
    ]

    print("=" * 70)
    print("HYBRID PRIORITY ENGINE V3")
    print("=" * 70)

    for complaint in test_complaints:

        result = predict_priority(complaint)

        print("\nComplaint:", complaint)
        print("Final Priority :", result["final_priority"])
        print("ML Priority    :", result["ml_priority"])
        print(
            "ML Confidence  :",
            f"{result['ml_confidence']:.2%}"
        )
        print(
            "Rule Priority  :",
            result["rule_priority"]
        )
        print(
            "Rule Score     :",
            result["rule_score"]
        )
        print(
            "Decision Method:",
            result["method"]
        )