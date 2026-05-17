import os
import re
import pandas as pd


CSV_PATH = r"D:\search-engine-(1)\search_engine_project\data\medicine_dataset.csv"
SEARCH_FOLDER = "documents"
DISPLAY_FOLDER = "display_documents"
MAX_DOCS = 100


def clean_filename(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def safe_value(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def collect_columns(row, keywords):
    values = []

    for col in row.index:
        col_lower = col.lower()

        for keyword in keywords:
            if keyword in col_lower:
                value = safe_value(row[col])
                if value:
                    values.append(value)

    return values


def row_to_search_document(row):
    drug_name = safe_value(row.get("name", ""))

    uses = collect_columns(row, ["use"])
    substitutes = collect_columns(row, ["substitute"])
    therapeutic_class = collect_columns(row, ["therapeutic"])
    action_class = collect_columns(row, ["action"])
    chemical_class = collect_columns(row, ["chemical"])
    drug_class = collect_columns(row, ["class"])

    text = f"""
Drug Name: {drug_name}

Medicine Information:
{drug_name} is a medicine.

Uses:
{", ".join(uses)}

Substitutes:
{", ".join(substitutes)}

Therapeutic Class:
{", ".join(therapeutic_class)}

Action Class:
{", ".join(action_class)}

Chemical Class:
{", ".join(chemical_class)}

Drug Class:
{", ".join(drug_class)}
"""

    return text.strip()


def row_to_display_document(row):
    drug_name = safe_value(row.get("name", ""))

    uses = collect_columns(row, ["use"])
    side_effects = collect_columns(row, ["side"])
    substitutes = collect_columns(row, ["substitute"])
    therapeutic_class = collect_columns(row, ["therapeutic"])
    action_class = collect_columns(row, ["action"])
    chemical_class = collect_columns(row, ["chemical"])
    habit_forming = safe_value(row.get("Habit Forming", ""))

    text = f"""
Drug Name: {drug_name}

Uses:
{", ".join(uses)}

Side Effects:
{", ".join(side_effects)}

Substitutes:
{", ".join(substitutes)}

Therapeutic Class:
{", ".join(therapeutic_class)}

Action Class:
{", ".join(action_class)}

Chemical Class:
{", ".join(chemical_class)}

Habit Forming:
{habit_forming}
"""

    return text.strip()


def convert_csv_to_txt():
    os.makedirs(SEARCH_FOLDER, exist_ok=True)
    os.makedirs(DISPLAY_FOLDER, exist_ok=True)

    df = pd.read_csv(CSV_PATH)

    print("Dataset columns:")
    print(df.columns.tolist())

    for i, (_, row) in enumerate(df.head(MAX_DOCS).iterrows(), start=1):
        drug_name = safe_value(row.get("name", f"drug_{i}"))

        filename = f"doc{i}_{clean_filename(drug_name)}.txt"

        search_path = os.path.join(SEARCH_FOLDER, filename)
        display_path = os.path.join(DISPLAY_FOLDER, filename)

        with open(search_path, "w", encoding="utf-8") as file:
            file.write(row_to_search_document(row))

        with open(display_path, "w", encoding="utf-8") as file:
            file.write(row_to_display_document(row))

    print(f"{MAX_DOCS} search documents created in '{SEARCH_FOLDER}'.")
    print(f"{MAX_DOCS} display documents created in '{DISPLAY_FOLDER}'.")


if __name__ == "__main__":
    convert_csv_to_txt()