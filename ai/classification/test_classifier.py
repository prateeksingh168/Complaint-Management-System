import joblib

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "preprocessing"))

from text_preprocessing import clean_text

MODEL_PATH = "ai/models/complaint_category_model.pkl"
VECTORIZER_PATH = "ai/models/tfidf_vectorizer.pkl"


model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


test_complaints = [
    {
        "text": "I paid for my purchase but the transaction is showing twice",
        "expected": "Billing",
    },
    {
        "text": "The website freezes whenever I open my dashboard",
        "expected": "Technical",
    },
    {
        "text": "I cannot remember my password and cannot sign in",
        "expected": "Account",
    },
    {
        "text": "My parcel has not arrived even though the delivery date has passed",
        "expected": "Delivery",
    },
    {
        "text": "The support service I received did not solve my problem",
        "expected": "Service",
    },
    {
        "text": "I want to know how the complaint process works",
        "expected": "Other",
    },
]


print("=" * 60)
print("CUSTOM COMPLAINT CLASSIFICATION TEST")
print("=" * 60)


correct = 0

for item in test_complaints:

    cleaned_text = clean_text(item["text"])

    vector = vectorizer.transform([cleaned_text])

    prediction = model.predict(vector)[0]

    result = "PASS" if prediction == item["expected"] else "FAIL"

    if result == "PASS":
        correct += 1

    print("\nComplaint:", item["text"])
    print("Expected :", item["expected"])
    print("Predicted:", prediction)
    print("Result   :", result)


accuracy = correct / len(test_complaints)

print("\n" + "=" * 60)
print(f"Custom Test Accuracy: {accuracy:.2%}")
print("=" * 60)