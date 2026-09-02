from complexity_engine_v2 import predict_complexity


# --------------------------------------------------
# 15 Unseen Complaints
# --------------------------------------------------

test_cases = [
    (
        "The entire platform is down and I cannot access any service.",
        "High"
    ),
    (
        "Several important features are failing repeatedly and blocking my work.",
        "High"
    ),
    (
        "I cannot complete my payment because the system keeps rejecting it.",
        "High"
    ),
    (
        "My delivery is taking longer than expected.",
        "Medium"
    ),
    (
        "I need some information about changing my account details.",
        "Low"
    ),
    (
        "The website has a small display issue on my profile page.",
        "Low"
    ),
    (
        "Multiple attempts to reset my password have failed.",
        "High"
    ),
    (
        "The service is completely unavailable for all users.",
        "High"
    ),
    (
        "My invoice contains an incorrect amount and needs to be corrected.",
        "Medium"
    ),
    (
        "I have a simple question about the complaint procedure.",
        "Low"
    ),
    (
        "The application crashes whenever I try to submit a request.",
        "High"
    ),
    (
        "My order is slightly delayed but I can still wait.",
        "Medium"
    ),
    (
        "I cannot access my account and several login attempts are failing.",
        "High"
    ),
    (
        "I need general guidance about using the service.",
        "Low"
    ),
    (
        "A major system problem is preventing me from completing my work.",
        "High"
    )
]


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

print("=" * 75)
print("HYBRID COMPLEXITY ENGINE V1 - EVALUATION")
print("=" * 75)

correct = 0

for complaint, expected in test_cases:

    result = predict_complexity(complaint)

    predicted = result["complexity"]

    if predicted == expected:
        status = "PASS"
        correct += 1
    else:
        status = "FAIL"

    print("\nComplaint:", complaint)
    print("Expected :", expected)
    print("Predicted:", predicted)
    print("Result   :", status)
    print("Method   :", result["decision_method"])


# --------------------------------------------------
# Final Accuracy
# --------------------------------------------------

total = len(test_cases)

accuracy = (correct / total) * 100

print("\n" + "=" * 75)
print("FINAL EVALUATION")
print("=" * 75)

print(f"Correct Predictions: {correct}/{total}")
print(f"Accuracy: {accuracy:.2f}%")

print("=" * 75)