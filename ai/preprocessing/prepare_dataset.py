import pandas as pd

from text_preprocessing import clean_text


# Input and output paths
INPUT_PATH = "ai/data/complaint_management_dataset.csv"
OUTPUT_PATH = "ai/data/complaint_management_dataset_cleaned.csv"


def prepare_dataset():
    # Load original dataset
    df = pd.read_csv(INPUT_PATH)

    print("Original dataset shape:", df.shape)

    # Apply the common preprocessing function
    df["cleaned_complaint_text"] = df["complaint_text"].apply(clean_text)

    # Save cleaned dataset
    df.to_csv(OUTPUT_PATH, index=False)

    print("Cleaned dataset saved successfully.")
    print("Output path:", OUTPUT_PATH)
    print("Final dataset shape:", df.shape)

    # Display sample
    print("\nSample:")
    print(
        df[
            [
                "complaint_text",
                "cleaned_complaint_text",
                "category",
                "priority",
            ]
        ].head()
    )


if __name__ == "__main__":
    prepare_dataset()