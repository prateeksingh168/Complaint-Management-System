import uuid
from datetime import datetime

from pathlib import Path
import sys

# Allow imports from sibling AI modules
AI_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(AI_DIR / "preprocessing"))
sys.path.append(str(AI_DIR / "classification"))
sys.path.append(str(AI_DIR / "priority"))
sys.path.append(str(AI_DIR / "assignment"))

from text_preprocessing import clean_text
from priority_engine_v3 import predict_priority
from assignment_engine import assign_ticket

import joblib


# --------------------------------------------------
# Model Paths
# --------------------------------------------------

CATEGORY_MODEL_PATH = (
    "ai/models/complaint_category_model.pkl"
)

CATEGORY_VECTORIZER_PATH = (
    "ai/models/tfidf_vectorizer.pkl"
)


# --------------------------------------------------
# Load Category Model
# --------------------------------------------------

category_model = joblib.load(
    CATEGORY_MODEL_PATH
)

category_vectorizer = joblib.load(
    CATEGORY_VECTORIZER_PATH
)


# --------------------------------------------------
# Category Prediction
# --------------------------------------------------

def predict_category(complaint_text):
    """Predict complaint category."""

    cleaned_text = clean_text(
        complaint_text
    )

    vector = category_vectorizer.transform(
        [cleaned_text]
    )

    prediction = category_model.predict(
        vector
    )[0]

    return prediction


# --------------------------------------------------
# Complexity Estimation
# --------------------------------------------------

def estimate_complexity(
    complaint_text,
    priority
):
    """
    Estimate complaint complexity.

    This is a simple initial heuristic.
    Later it can be replaced with a trained
    complexity model.
    """

    text = complaint_text.lower()

    high_complexity_indicators = [
        "completely unavailable",
        "critical",
        "service outage",
        "entire service is down",
        "multiple",
        "repeatedly",
    ]

    medium_complexity_indicators = [
        "problem",
        "issue",
        "delayed",
        "incorrect",
        "unable",
    ]

    if (
        priority == "Urgent"
        or any(
            indicator in text
            for indicator in high_complexity_indicators
        )
    ):
        return "High"

    if any(
        indicator in text
        for indicator in medium_complexity_indicators
    ):
        return "Medium"

    return "Low"


# --------------------------------------------------
# Generate AI Ticket
# --------------------------------------------------

def generate_ticket(complaint_text):
    """
    Convert a natural-language complaint
    into an AI-generated ticket.
    """

    # 1. Clean complaint
    cleaned_text = clean_text(
        complaint_text
    )

    # 2. Category
    category = predict_category(
        complaint_text
    )

    # 3. Priority
    priority_result = predict_priority(
        complaint_text
    )

    priority = priority_result[
        "final_priority"
    ]

    # 4. Complexity
    complexity = estimate_complexity(
        complaint_text,
        priority
    )

    # 5. Team assignment
    assignment = assign_ticket(
        category,
        priority,
        complexity
    )

    # 6. Generate ticket ID
    ticket_id = (
        "TKT-"
        + uuid.uuid4().hex[:8].upper()
    )

    # 7. Ticket creation time
    created_at = datetime.now().isoformat(
        timespec="seconds"
    )

    # 8. Final ticket
    ticket = {
        "ticket_id": ticket_id,
        "complaint_text": complaint_text,
        "cleaned_text": cleaned_text,
        "category": category,
        "priority": priority,
        "complexity": complexity,
        "recommended_team": assignment[
            "recommended_team"
        ],
        "assignment_score": assignment[
            "assignment_score"
        ],
        "assignment_reason": assignment[
            "reason"
        ],
        "priority_method": priority_result[
            "method"
        ],
        "created_at": created_at,
        "status": "Registered",
    }

    return ticket


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    complaint = (
        "My payment was deducted twice "
        "and I need urgent help."
    )

    ticket = generate_ticket(
        complaint
    )

    print("=" * 70)
    print("AI-GENERATED COMPLAINT TICKET")
    print("=" * 70)

    for key, value in ticket.items():

        print(
            f"{key}: {value}"
        )