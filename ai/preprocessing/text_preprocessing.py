import re


def clean_text(text: str) -> str:
    """
    Clean complaint text for NLP/ML processing.

    Steps:
    1. Handle missing/non-string input.
    2. Convert text to lowercase.
    3. Remove URLs.
    4. Remove special characters and punctuation.
    5. Normalize multiple spaces.
    6. Return cleaned text.
    """

    if not isinstance(text, str):
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Keep letters, numbers and spaces
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


if __name__ == "__main__":
    sample_complaint = "My Payment FAILED!!! Please Help."

    cleaned_complaint = clean_text(sample_complaint)

    print("Original Complaint:")
    print(sample_complaint)

    print("\nCleaned Complaint:")
    print(cleaned_complaint)