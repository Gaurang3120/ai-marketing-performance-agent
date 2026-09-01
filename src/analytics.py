import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "marketing.db"

def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def get_campaign_summary():
    conn = get_connection()
    query = """
    SELECT
        COUNT(*) AS total_campaigns,
        SUM(impressions) AS total_impressions,
        SUM(clicks) AS total_clicks,
        SUM(conversions) AS total_conversions,
        SUM(ad_spend) AS total_spend,
        SUM(revenue) AS total_revenue,
        SUM(profit) AS total_profit,
        AVG(CTR) AS average_ctr,
        AVG(CPC) AS average_cpc,
        AVG(conversion_rate) AS average_conversion_rate,
        AVG(CPA) AS average_cpa,
        AVG(ROAS) AS average_roas
    FROM campaigns
    """
    summary = pd.read_sql_query(query, conn)
    conn.close()
    return summary

def get_platform_performance():
    conn = get_connection()
    query = """
    SELECT
        platform,
        COUNT(*) AS campaigns,
        SUM(impressions) AS impressions,
        SUM(clicks) AS clicks,
        SUM(conversions) AS conversions,
        SUM(ad_spend) AS spend,
        SUM(revenue) AS revenue,
        SUM(profit) AS profit,
        AVG(CTR) AS avg_ctr,
        AVG(CPC) AS avg_cpc,
        AVG(conversion_rate) AS avg_conversion_rate,
        AVG(CPA) AS avg_cpa,
        AVG(ROAS) AS avg_roas
    FROM campaigns
    GROUP BY platform
    ORDER BY avg_roas DESC
    """
    performance = pd.read_sql_query(query, conn)
    conn.close()
    return performance

def get_underperforming_campaigns():
    conn = get_connection()
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
    WHERE ROAS < 1
       OR profit < 0
       OR conversion_rate < 1
    ORDER BY profit ASC
    """
    campaigns = pd.read_sql_query(query, conn)
    conn.close()
    return campaigns

def get_objective_performance():

    conn = get_connection()

    query = """
    SELECT
        campaign_objective,
        COUNT(*) AS campaigns,
        AVG(CTR) AS avg_ctr,
        AVG(CPC) AS avg_cpc,
        AVG(conversion_rate) AS avg_conversion_rate,
        AVG(CPA) AS avg_cpa,
        AVG(ROAS) AS avg_roas,
        AVG(profit) AS avg_profit
    FROM campaigns
    GROUP BY campaign_objective
    ORDER BY avg_roas DESC
    """

    performance = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return performance




if __name__ == "__main__":

    print("\n========== OVERALL PERFORMANCE ==========\n")

    summary = get_campaign_summary()
    print(summary.to_string(index=False))

    print("\n========== PLATFORM PERFORMANCE ==========\n")

    platform_data = get_platform_performance()
    print(platform_data.to_string(index=False))

    print("\n========== UNDERPERFORMING CAMPAIGNS ==========\n")

    weak_campaigns = get_underperforming_campaigns()

    print(
        weak_campaigns.head(10).to_string(index=False)
    )

    print("\n========== OBJECTIVE PERFORMANCE ==========\n")

    objective_data = get_objective_performance()

    print(
    objective_data.to_string(index=False)
    )
