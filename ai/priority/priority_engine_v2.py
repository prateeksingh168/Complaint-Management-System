import re
import joblib


MODEL_PATH = "ai/models/complaint_priority_model.pkl"
VECTORIZER_PATH = "ai/models/priority_tfidf_vectorizer.pkl"


# Load trained ML model
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


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
    """Calculate priority using predefined urgency indicators."""

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


def predict_ml_priority(text):
    """Return ML prediction and confidence."""

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
    Hybrid priority prediction using
    ML prediction, confidence and urgency rules.
    """

    rule_priority, rule_score = calculate_rule_priority(text)

    ml_priority, ml_confidence = predict_ml_priority(text)

    # Strong urgency indicators override ML
    if rule_priority == "Urgent":

        return {
            "final_priority": "Urgent",
            "ml_priority": ml_priority,
            "ml_confidence": ml_confidence,
            "rule_priority": rule_priority,
            "rule_score": rule_score,
            "method": "Strong Urgency Override",
        }

    # If ML and rule agree
    if rule_priority == ml_priority:

        return {
            "final_priority": ml_priority,
            "ml_priority": ml_priority,
            "ml_confidence": ml_confidence,
            "rule_priority": rule_priority,
            "rule_score": rule_score,
            "method": "Rule + ML Agreement",
        }

    # Strong ML confidence when no urgent rule exists
    if ml_confidence >= 0.70:

        return {
            "final_priority": ml_priority,
            "ml_priority": ml_priority,
            "ml_confidence": ml_confidence,
            "rule_priority": rule_priority,
            "rule_score": rule_score,
            "method": "High ML Confidence",
        }

    # Rule takes preference when ML confidence is low
    if rule_priority is not None:

        return {
            "final_priority": rule_priority,
            "ml_priority": ml_priority,
            "ml_confidence": ml_confidence,
            "rule_priority": rule_priority,
            "rule_score": rule_score,
            "method": "Rule Priority",
        }

    # Fallback to ML
    return {
        "final_priority": ml_priority,
        "ml_priority": ml_priority,
        "ml_confidence": ml_confidence,
        "rule_priority": None,
        "rule_score": 0,
        "method": "ML Fallback",
    }


if __name__ == "__main__":

    test_complaints = [
        "My entire service is completely unavailable.",
        "This is a critical issue and needs immediate attention.",
        "My application is repeatedly failing.",
        "This is a serious problem affecting my work.",
        "My delivery is delayed.",
        "My payment amount is incorrect.",
        "The website is not working properly.",
        "I have a question about the complaint process.",
        "I need general information about the service.",
        "I need guidance regarding my account.",
        "My service is completely unavailable and I cannot use it.",
        "The application has a major issue.",
        "I have a minor problem with my request.",
        "I need help with a delayed service.",
        "The system has a critical service outage.",
    ]

    print("=" * 70)
    print("HYBRID PRIORITY ENGINE V2")
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
        print("Decision Method:", result["method"])