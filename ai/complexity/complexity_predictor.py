import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# --------------------------------------------------
# Paths
# --------------------------------------------------

DATA_PATH = "ai/data/complaint_management_dataset_v2.csv"

MODEL_PATH = "ai/models/complaint_complexity_model.pkl"

VECTORIZER_PATH = "ai/models/complexity_tfidf_vectorizer.pkl"


# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)


# Keep required columns
df = df[["complaint_text", "complexity"]].dropna()


# --------------------------------------------------
# Features and Target
# --------------------------------------------------

X = df["complaint_text"]
y = df["complexity"]


# --------------------------------------------------
# Train/Test Split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# --------------------------------------------------
# TF-IDF
# --------------------------------------------------

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    max_features=5000
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(
    "TF-IDF training shape:",
    X_train_tfidf.shape
)


# --------------------------------------------------
# Train Model
# --------------------------------------------------

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

model.fit(
    X_train_tfidf,
    y_train
)


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

predictions = model.predict(
    X_test_tfidf
)

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\n" + "=" * 60)
print("COMPLEXITY MODEL EVALUATION")
print("=" * 60)

print(
    f"\nAccuracy: {accuracy:.4f}"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions
    )
)

print("Confusion Matrix:")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)


# --------------------------------------------------
# Save Model
# --------------------------------------------------

joblib.dump(
    model,
    MODEL_PATH
)

joblib.dump(
    vectorizer,
    VECTORIZER_PATH
)

print("\n" + "=" * 60)
print("COMPLEXITY MODEL SAVED")
print("=" * 60)

print(
    "Model:",
    MODEL_PATH
)

print(
    "Vectorizer:",
    VECTORIZER_PATH
)


# --------------------------------------------------
# Sample Prediction
# --------------------------------------------------

sample_complaint = (
    "The entire service is unavailable "
    "and the issue is affecting multiple users."
)

sample_vector = vectorizer.transform(
    [sample_complaint]
)

sample_prediction = model.predict(
    sample_vector
)[0]

print("\n" + "=" * 60)
print("SAMPLE COMPLEXITY PREDICTION")
print("=" * 60)

print(
    "Complaint:",
    sample_complaint
)

print(
    "Predicted Complexity:",
    sample_prediction
)