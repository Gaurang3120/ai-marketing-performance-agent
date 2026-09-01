import sqlite3
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "marketing.db"


def load_campaigns():
    """Load campaign performance data from SQLite."""

    conn = sqlite3.connect(DATABASE_PATH)

    query = """
    SELECT
        campaign_id,
        campaign_objective,
        platform,
        ad_placement,
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


def calculate_priority(df):
    """Calculate campaign priority based on business risk."""

    df = df.copy()

    df["loss_impact"] = df["profit"].apply(
        lambda x: abs(x) if x < 0 else 0
    )

    max_loss = df["loss_impact"].max()

    if max_loss > 0:
        df["loss_score"] = (
            df["loss_impact"] / max_loss
        )
    else:
        df["loss_score"] = 0


    df["roas_risk"] = df["ROAS"].apply(
        lambda x: min(max(0, 1 - x), 1)
    )



    # Higher CPA = higher risk.
    # Values above $5,000 are capped.

    df["cpa_risk"] = df["CPA"].apply(
        lambda x: min(max(0, x / 5000), 1)
    )


    df["conversion_risk"] = df["conversion_rate"].apply(
        lambda x: min(
            max(0, 5 - x) / 5,
            1
        )
    )

    df["priority_score"] = (
        df["loss_score"] * 0.50
        + df["roas_risk"] * 0.20
        + df["cpa_risk"] * 0.15
        + df["conversion_risk"] * 0.15
    )



    df["priority_score"] = df["priority_score"].clip(
        0,
        1
    )

    df["priority"] = pd.cut(
        df["priority_score"],
        bins=[
            -0.01,
            0.25,
            0.50,
            0.75,
            1.0
        ],
        labels=[
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        ]
    )


    df = df.sort_values(
        by="priority_score",
        ascending=False
    )

    return df


def get_priority_campaigns():

    df = load_campaigns()

    df = calculate_priority(df)

    return df


if __name__ == "__main__":

    print(
        "\n========== CAMPAIGN PRIORITIZATION ==========\n"
    )

    df = get_priority_campaigns()

    columns_to_show = [
        "campaign_id",
        "platform",
        "ROAS",
        "CPA",
        "profit",
        "priority_score",
        "priority"
    ]
    print(
        df[columns_to_show]
        .head(20)
        .to_string(index=False)
    )

    print(
        "\n========== PRIORITY SUMMARY ==========\n"
    )

    summary = (
        df["priority"]
        .value_counts()
        .sort_index()
    )

    print(summary)

    top_campaign = df.iloc[0]

    print(
        "\n========== TOP PRIORITY CAMPAIGN ==========\n"
    )

    print(
        f"Campaign ID     : {top_campaign['campaign_id']}"
    )

    print(
        f"Platform        : {top_campaign['platform']}"
    )

    print(
        f"ROAS            : {top_campaign['ROAS']}"
    )

    print(
        f"CPA             : ${top_campaign['CPA']:.2f}"
    )

    print(
        f"Profit          : ${top_campaign['profit']:.2f}"
    )

    print(
        f"Priority Score  : {top_campaign['priority_score']:.2f}"
    )

    print(
        f"Priority        : {top_campaign['priority']}"
    )
