import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

DATA_PATH = "ai/data/complaint_management_dataset_v2.csv"
MODEL_DIR = "ai/models"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "complaint_priority_model.pkl"
)

VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "priority_tfidf_vectorizer.pkl"
)


# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)

df = df.dropna(
    subset=[
        "cleaned_complaint_text",
        "priority"
    ]
)

X = df["cleaned_complaint_text"]
y = df["priority"]


# --------------------------------------------------
# Train-Test Split
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
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.95
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(
    "TF-IDF training shape:",
    X_train_tfidf.shape
)


# --------------------------------------------------
# Train Priority Model
# --------------------------------------------------

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train_tfidf, y_train)


# --------------------------------------------------
# Prediction
# --------------------------------------------------

y_pred = model.predict(X_test_tfidf)


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n" + "=" * 50)
print("PRIORITY MODEL EVALUATION")
print("=" * 50)

print(f"\nAccuracy: {accuracy:.4f}")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred
    )
)

print("Confusion Matrix:")
print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# --------------------------------------------------
# Save Model
# --------------------------------------------------

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_PATH
)

joblib.dump(
    vectorizer,
    VECTORIZER_PATH
)

print("\n" + "=" * 50)
print("PRIORITY MODEL SAVED")
print("=" * 50)

print("Model:", MODEL_PATH)
print(
    "Vectorizer:",
    VECTORIZER_PATH
)


# --------------------------------------------------
# Sample Prediction
# --------------------------------------------------

sample_complaint = (
    "The entire service is completely unavailable "
    "and I cannot use it."
)

sample_tfidf = vectorizer.transform(
    [sample_complaint]
)

prediction = model.predict(
    sample_tfidf
)[0]

print("\n" + "=" * 50)
print("SAMPLE PRIORITY PREDICTION")
print("=" * 50)

print(
    "Complaint:",
    sample_complaint
)

print(
    "Predicted Priority:",
    prediction
)