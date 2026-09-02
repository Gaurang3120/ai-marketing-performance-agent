import os
import sqlite3
from pathlib import Path
from typing import Optional, TypedDict

import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "marketing.db"

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found. Add GOOGLE_API_KEY to the .env file."
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
)


class MarketingState(TypedDict, total=False):
    campaign_id: str
    campaign_data: dict

    anomaly_detected: bool
    anomaly_reasons: str

    priority_score: float
    priority: str

    performance_analysis: str
    root_cause: str
    recommendation: str

    human_approval: Optional[str]
    audit_status: str


def load_campaign(state: MarketingState):
    campaign_id = state.get("campaign_id")

    if not campaign_id:
        raise ValueError("campaign_id is required.")

    conn = sqlite3.connect(DATABASE_PATH)

    try:
        df = pd.read_sql_query(
            """
            SELECT *
            FROM campaigns
            WHERE campaign_id = ?
            """,
            conn,
            params=(campaign_id,),
        )
    finally:
        conn.close()

    if df.empty:
        raise ValueError(f"Campaign {campaign_id} not found.")

    campaign = df.iloc[0].to_dict()

    print(f"\nCampaign {campaign_id} loaded successfully.")

    return {"campaign_data": campaign}


def detect_anomaly(state: MarketingState):
    campaign = state["campaign_data"]
    reasons = []

    if campaign["profit"] < 0:
        reasons.append("Negative profit")

    if campaign["ROAS"] < 1:
        reasons.append("ROAS below 1")

    if campaign["conversion_rate"] < 1:
        reasons.append("Very low conversion rate")

    if campaign["CPA"] > 500:
        reasons.append("High CPA")

    anomaly_detected = bool(reasons)
    anomaly_reasons = ", ".join(reasons)

    print("\n========== ANOMALY DETECTION ==========")
    print(f"Anomaly detected: {anomaly_detected}")

    if anomaly_reasons:
        print(f"Reasons: {anomaly_reasons}")

    return {
        "anomaly_detected": anomaly_detected,
        "anomaly_reasons": anomaly_reasons,
    }


def prioritize_campaign(state: MarketingState):
    campaign = state["campaign_data"]

    if not state["anomaly_detected"]:
        return {
            "priority_score": 0.0,
            "priority": "LOW",
        }

    profit = campaign["profit"]

    if profit < 0:
        loss_score = min(abs(profit) / 40000, 1)
    else:
        loss_score = 0

    roas = campaign["ROAS"]
    roas_risk = min(max(0, 1 - roas), 1)

    cpa = campaign["CPA"]
    cpa_risk = min(max(0, cpa / 5000), 1)

    conversion_rate = campaign["conversion_rate"]
    conversion_risk = min(
        max(0, 5 - conversion_rate) / 5,
        1,
    )

    priority_score = (
        loss_score * 0.50
        + roas_risk * 0.20
        + cpa_risk * 0.15
        + conversion_risk * 0.15
    )

    priority_score = min(max(priority_score, 0), 1)

    if priority_score >= 0.75:
        priority = "CRITICAL"
    elif priority_score >= 0.50:
        priority = "HIGH"
    elif priority_score >= 0.25:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    print("\n========== PRIORITIZATION ==========")
    print(f"Priority Score: {priority_score:.2f}")
    print(f"Priority: {priority}")

    return {
        "priority_score": priority_score,
        "priority": priority,
    }


def analyze_performance(state: MarketingState):
    campaign = state["campaign_data"]

    prompt = f"""
You are an expert AI Marketing Performance Analyst.

Analyze the following marketing campaign using ONLY
the provided campaign data.

STRICT RULES:
- Do not invent facts.
- Do not assume missing information.
- Do not create fake industry benchmarks.
- Do not use external statistics.
- Base every conclusion on the provided data.

CAMPAIGN DATA:

Campaign ID:
{campaign.get("campaign_id")}

Campaign Objective:
{campaign.get("campaign_objective")}

Platform:
{campaign.get("platform")}

Ad Placement:
{campaign.get("ad_placement")}

Impressions:
{campaign.get("impressions")}

Clicks:
{campaign.get("clicks")}

Conversions:
{campaign.get("conversions")}

Ad Spend:
{campaign.get("ad_spend")}

Revenue:
{campaign.get("revenue")}

Profit:
{campaign.get("profit")}

CTR:
{campaign.get("CTR")}

CPC:
{campaign.get("CPC")}

Conversion Rate:
{campaign.get("conversion_rate")}

CPA:
{campaign.get("CPA")}

ROAS:
{campaign.get("ROAS")}

Quality Score:
{campaign.get("quality_score")}

Creative Age:
{campaign.get("creative_age_days")}

Purchase Intent Score:
{campaign.get("purchase_intent_score")}

Bounce Rate:
{campaign.get("bounce_rate")}

Average Session Duration:
{campaign.get("avg_session_duration_seconds")}

Provide a concise business-focused diagnosis.

Use exactly this structure:

1. PERFORMANCE SUMMARY

2. STRONG SIGNALS

3. WEAK SIGNALS

4. MOST IMPORTANT BUSINESS PROBLEM
"""

    response = llm.invoke(prompt)
    analysis = response.content

    print("\n========== AI PERFORMANCE ANALYSIS ==========\n")
    print(analysis)

    return {"performance_analysis": analysis}


def analyze_root_cause(state: MarketingState):
    campaign = state["campaign_data"]
    performance_analysis = state["performance_analysis"]

    prompt = f"""
You are an AI marketing root-cause analyst.

Determine the PRIMARY root cause of this campaign's
underperformance.

Use ONLY the campaign data and performance analysis
provided below.

STRICT RULES:
- Do not invent information.
- Do not assume missing facts.
- Do not mention external industry statistics.
- Every claim must be supported by campaign data.

CAMPAIGN DATA:

{campaign}

PERFORMANCE ANALYSIS:

{performance_analysis}

Return exactly this structure:

PRIMARY ROOT CAUSE:
<one clear root cause>

EVIDENCE:
- <data-based evidence>
- <data-based evidence>
- <data-based evidence>

SECONDARY FACTORS:
- <factor>
- <factor>

CONFIDENCE:
High / Medium / Low
"""

    response = llm.invoke(prompt)
    root_cause = response.content

    print("\n========== AI ROOT CAUSE ==========\n")
    print(root_cause)

    return {"root_cause": root_cause}


def generate_recommendation(state: MarketingState):
    campaign = state["campaign_data"]
    root_cause = state["root_cause"]

    prompt = f"""
You are an AI marketing optimization strategist.

Create practical recommendations for the campaign.

CAMPAIGN DATA:

{campaign}

ROOT CAUSE:

{root_cause}

STRICT RULES:

1. Recommendations must be directly connected
   to the campaign data.

2. Do not invent company information.

3. Do not promise guaranteed financial results.

4. Separate immediate actions from experiments.

5. Prioritize actions with the highest likely
   business impact.

6. Keep recommendations practical and specific.

Return exactly this structure:

IMMEDIATE ACTIONS:

1.
2.
3.

EXPERIMENTS:

1.
2.

METRICS TO MONITOR:

1.
2.
3.
"""

    response = llm.invoke(prompt)
    recommendation = response.content

    print("\n========== AI RECOMMENDATION ==========\n")
    print(recommendation)

    return {"recommendation": recommendation}


def human_approval(state: MarketingState):
    print("\n========== HUMAN APPROVAL ==========")
    print("Waiting for Streamlit approval...")

    # Streamlit handles the approval step.
    return {"human_approval": "PENDING"}


def save_audit(state: MarketingState):
    conn = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS campaign_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT,
                priority TEXT,
                priority_score REAL,
                root_cause TEXT,
                recommendation TEXT,
                human_approval TEXT
            )
            """
        )

        cursor.execute(
            """
            INSERT INTO campaign_audit (
                campaign_id,
                priority,
                priority_score,
                root_cause,
                recommendation,
                human_approval
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                state["campaign_data"]["campaign_id"],
                state["priority"],
                state["priority_score"],
                state["root_cause"],
                state["recommendation"],
                state["human_approval"],
            ),
        )

        conn.commit()
    finally:
        conn.close()

    print("\n========== AUDIT TRAIL ==========")
    print("Decision saved successfully.")

    return {"audit_status": "SAVED"}


graph = StateGraph(MarketingState)

graph.add_node("load_campaign", load_campaign)
graph.add_node("detect_anomaly", detect_anomaly)
graph.add_node("prioritize_campaign", prioritize_campaign)
graph.add_node("analyze_performance", analyze_performance)
graph.add_node("analyze_root_cause", analyze_root_cause)
graph.add_node("generate_recommendation", generate_recommendation)
graph.add_node("human_approval", human_approval)
graph.add_node("save_audit", save_audit)

graph.set_entry_point("load_campaign")

graph.add_edge("load_campaign", "detect_anomaly")
graph.add_edge("detect_anomaly", "prioritize_campaign")
graph.add_edge("prioritize_campaign", "analyze_performance")
graph.add_edge("analyze_performance", "analyze_root_cause")
graph.add_edge("analyze_root_cause", "generate_recommendation")
graph.add_edge("generate_recommendation", "human_approval")

# Streamlit handles the actual approval step.
graph.add_edge("human_approval", END)


app = graph.compile()


if __name__ == "__main__":
    print("\n============================================")
    print(" AI MARKETING PERFORMANCE AGENT")
    print("============================================")

    campaign_id = input("\nEnter Campaign ID: ").strip()

    result = app.invoke({"campaign_id": campaign_id})

    print("\n============================================")
    print(" AI ANALYSIS COMPLETED")
    print("============================================")

    print(f"\nCampaign: {result['campaign_data']['campaign_id']}")
    print(f"Priority: {result['priority']}")
    print(f"Priority Score: {result['priority_score']:.2f}")
    print(f"Human Decision: {result['human_approval']}")

