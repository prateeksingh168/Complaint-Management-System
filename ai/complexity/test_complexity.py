import joblib
from sklearn.metrics import accuracy_score


# --------------------------------------------------
# Load trained model and vectorizer
# --------------------------------------------------

MODEL_PATH = "ai/models/complaint_complexity_model.pkl"
VECTORIZER_PATH = "ai/models/complexity_tfidf_vectorizer.pkl"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


# --------------------------------------------------
# 15 Unseen Complaints
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
# Expected Complexity
# --------------------------------------------------

expected_complexity = [
    "High",
    "High",
    "High",
    "Medium",
    "Low",
    "Low",
    "High",
    "High",
    "Medium",
    "Low",
    "High",
    "Medium",
    "High",
    "Low",
    "High"
]


# --------------------------------------------------
# Prediction
# --------------------------------------------------

X_test = vectorizer.transform(test_complaints)

predictions = model.predict(X_test)


# --------------------------------------------------
# Display Results
# --------------------------------------------------

print("=" * 75)
print("CUSTOM COMPLEXITY CLASSIFICATION TEST")
print("=" * 75)

correct = 0

for complaint, expected, predicted in zip(
    test_complaints,
    expected_complexity,
    predictions
):

    result = "PASS" if expected == predicted else "FAIL"

    if result == "PASS":
        correct += 1

    print("\nComplaint:", complaint)
    print("Expected :", expected)
    print("Predicted:", predicted)
    print("Result   :", result)


# --------------------------------------------------
# Accuracy
# --------------------------------------------------

accuracy = accuracy_score(
    expected_complexity,
    predictions
)

print("\n" + "=" * 75)
print(
    f"Custom Test Accuracy: {accuracy * 100:.2f}%"
)
print("=" * 75)

print(
    f"Correct Predictions: {correct}/15"
)