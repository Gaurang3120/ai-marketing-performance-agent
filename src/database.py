import sqlite3
from pathlib import Path
from data_loader import load_campaign_data

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "marketing.db"
def create_database():
    df = load_campaign_data()
    conn = sqlite3.connect(DATABASE_PATH)
    df.to_sql(
        "campaigns",
        conn,
        if_exists="replace",
        index=False
    )
    conn.close()
    print("SQLite database created successfully.")
    print(f"Database: {DATABASE_PATH}")
    print(f"Records stored: {len(df)}")

if __name__ == "__main__":
    create_database()