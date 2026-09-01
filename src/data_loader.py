import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "campaigns_dataset.csv"

def load_campaign_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_PATH}"
        )
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    df = df.dropna(how="all")
    df = df.drop_duplicates(subset=["campaign_id"])
    numeric_columns = [
        "impressions",
        "clicks",
        "spend",
        "conversions",
        "revenue",
        "CTR",
        "CPC",
        "conversion_rate",
        "CPA",
        "ROAS",
        "profit",
    ]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )
    return df


if __name__ == "__main__":
    df = load_campaign_data()

    print("Campaign data loaded successfully.")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 records:")
    print(df.head())