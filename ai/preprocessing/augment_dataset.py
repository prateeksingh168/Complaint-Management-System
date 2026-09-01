import pandas as pd


INPUT_PATH = "ai/data/complaint_management_dataset_cleaned.csv"
OUTPUT_PATH = "ai/data/complaint_management_dataset_v2.csv"


# Targeted examples to improve Account vs Technical classification
new_examples = [
    ("I forgot my password and cannot log into my account.", "Account"),
    ("I am unable to sign in because my password is not working.", "Account"),
    ("I need to reset my account password.", "Account"),
    ("My account login is not accepting my password.", "Account"),
    ("I cannot log into my account with my credentials.", "Account"),
    ("I forgot my account password.", "Account"),
    ("My account sign in is not working.", "Account"),
    ("I cannot access my account because I forgot my password.", "Account"),

    ("The login page crashes when I try to sign in.", "Technical"),
    ("The application shows an error after I enter my credentials.", "Technical"),
    ("The website freezes during login.", "Technical"),
    ("The login screen is not loading.", "Technical"),
]


def main():
    df = pd.read_csv(INPUT_PATH)

    rows = []

    for index, (text, category) in enumerate(new_examples, start=1):
        rows.append({
            "complaint_id": f"AUG-{index:03d}",
            "complaint_text": text,
            "cleaned_complaint_text": text.lower(),
            "category": category,
            "priority": "Medium",
            "complexity": "Low",
            "recommended_team": (
                "Account Support"
                if category == "Account"
                else "Technical Support"
            ),
        })

    new_df = pd.DataFrame(rows)

    updated_df = pd.concat([df, new_df], ignore_index=True)

    updated_df.to_csv(OUTPUT_PATH, index=False)

    print("Original rows:", len(df))
    print("Added rows:", len(new_df))
    print("New total rows:", len(updated_df))
    print("Saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()