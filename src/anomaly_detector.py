import sqlite3
from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "marketing.db"

def load_campaigns():
    conn = sqlite3.connect(DATABASE_PATH)
    query = """
    SELECT
        campaign_id,
        campaign_objective,
        platform,
        ad_placement,
        device_type,
        impressions,
        clicks,
        conversions,
        ad_spend,
        revenue,
        CTR,
        CPC,
        conversion_rate,
        CPA,
        ROAS,
        profit
    FROM campaigns
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def detect_anomalies(df):
    features = [
        "CTR",
        "CPC",
        "conversion_rate",
        "CPA",
        "ROAS",
        "profit",
    ]
    model = IsolationForest(
        contamination=0.05,
        random_state=42
    )
    df["anomaly_prediction"] = model.fit_predict(
        df[features].fillna(0)
    )
    df["is_anomaly"] = df["anomaly_prediction"].apply(
        lambda value: value == -1
    )
    return df

def get_anomalies():
    df = load_campaigns()
    df = detect_anomalies(df)
    anomalies = df[df["is_anomaly"]].copy()
    anomalies = anomalies.sort_values(
        by="profit",
        ascending=True
    )
    return anomalies

if __name__ == "__main__":

    print("\nANOMALY DETECTION \n")

    anomalies = get_anomalies()

    print(f"Total anomalies detected: {len(anomalies)}")

    print("\nTop anomalous campaigns:\n")

    columns = [
        "campaign_id",
        "platform",
        "ROAS",
        "CPC",
        "conversion_rate",
        "CPA",
        "profit",
    ]

    print(
        anomalies[columns]
        .head(15)
        .to_string(index=False)
    )