import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agent import app, save_audit


st.set_page_config(
    page_title="AI Marketing Performance Agent",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7fb;
    }

    .main .block-container {
        color: #111827 !important;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main .block-container p,
    .main .block-container li,
    .main .block-container span,
    .main .block-container label {
        color: #111827 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #111827 !important;
    }

    .stCaption,
    [data-testid="stCaptionContainer"] {
        color: #4b5563 !important;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 16px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #374151 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #111827 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #374151 !important;
    }

    .ai-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 22px;
        margin-top: 8px;
        margin-bottom: 24px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }

    .ai-card,
    .ai-card p,
    .ai-card li,
    .ai-card span,
    .ai-card strong,
    .ai-card em,
    .ai-card div {
        color: #111827 !important;
    }

    .ai-card p {
        line-height: 1.65;
        margin-bottom: 10px;
    }

    .ai-card li {
        line-height: 1.6;
        margin-bottom: 6px;
    }

    .ai-card strong {
        font-weight: 700;
    }

    .section-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 20px;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .section-card p,
    .section-card li,
    .section-card span,
    .section-card div {
        color: #111827 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
    }

    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] .stCaption {
        color: #d1d5db !important;
    }

    div[data-baseweb="select"] {
        background-color: #ffffff !important;
    }

    div[data-baseweb="select"] * {
        color: #111827 !important;
    }

    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        min-height: 44px;
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    div[data-testid="stAlert"] p {
        color: inherit !important;
    }

    div[data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border-radius: 12px;
    }

    hr {
        border-color: #e5e7eb !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_database_path():
    possible_paths = [
        BASE_DIR / "data" / "marketing.db",
        BASE_DIR / "marketing.db",
        BASE_DIR / "src" / "marketing.db",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def get_campaign_table():
    db_path = get_database_path()

    if not db_path:
        return None

    conn = sqlite3.connect(db_path)

    tables = pd.read_sql_query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """,
        conn,
    )

    for table in tables["name"]:
        columns = pd.read_sql_query(
            f"PRAGMA table_info([{table}])",
            conn,
        )

        if "campaign_id" in columns["name"].tolist():
            conn.close()
            return table

    conn.close()
    return None


def get_campaign_ids():
    db_path = get_database_path()
    table = get_campaign_table()

    if not db_path or not table:
        return []

    conn = sqlite3.connect(db_path)

    df = pd.read_sql_query(
        f"""
        SELECT campaign_id
        FROM [{table}]
        ORDER BY campaign_id
        """,
        conn,
    )

    conn.close()

    return df["campaign_id"].astype(str).tolist()


def number(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def get_value(data, *keys, default=0):
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]

    return default


with st.sidebar:
    st.title("🤖 Marketing AI")
    st.caption("AI-powered campaign intelligence")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Campaign Analysis",
            "Performance Overview",
            "About Agent",
        ],
    )

    st.divider()

    st.markdown("### Agent Pipeline")
    st.write("🗄️ Campaign Data")
    st.write("↓")
    st.write("🔎 Anomaly Detection")
    st.write("↓")
    st.write("🎯 Prioritization")
    st.write("↓")
    st.write("🧠 AI Analysis")
    st.write("↓")
    st.write("🔬 Root Cause")
    st.write("↓")
    st.write("💡 Recommendation")
    st.write("↓")
    st.write("👤 Human Approval")
    st.write("↓")
    st.write("📋 Audit Trail")


st.title("📊 AI Marketing Performance Agent")

st.caption(
    "Autonomous campaign diagnostics, anomaly detection, "
    "root-cause analysis and AI-powered optimization."
)


if page == "Campaign Analysis":
    st.header("🎯 Campaign Analysis")

    campaign_ids = get_campaign_ids()

    if campaign_ids:
        campaign_id = st.selectbox(
            "Select Campaign",
            campaign_ids,
        )
    else:
        campaign_id = st.text_input(
            "Campaign ID",
            value="CAMP_00001",
        )

    analyze = st.button(
        "🚀 Analyze Campaign",
        type="primary",
        use_container_width=True,
    )

    if analyze:
        if not campaign_id:
            st.error("Please select a campaign.")
        else:
            with st.spinner("🤖 AI Agent is analyzing campaign..."):
                try:
                    result = app.invoke({"campaign_id": campaign_id})

                    st.session_state["result"] = result
                    st.session_state["campaign_id"] = campaign_id

                    st.session_state.pop("human_decision", None)
                    st.session_state.pop("audit_status", None)

                    st.success("✅ Campaign analysis completed.")

                except Exception as e:
                    st.error("❌ Agent execution failed.")
                    st.exception(e)

    if "result" in st.session_state:
        result = st.session_state["result"]

        campaign_id = st.session_state.get(
            "campaign_id",
            campaign_id,
        )

        campaign = result.get("campaign_data", {})

        if not isinstance(campaign, dict):
            campaign = {}

        st.divider()
        st.subheader("📋 Campaign Overview")

        platform = get_value(
            campaign,
            "platform",
            default="N/A",
        )

        objective = get_value(
            campaign,
            "campaign_objective",
            "objective",
            default="N/A",
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Campaign ID", campaign_id)

        with col2:
            st.metric("Platform", platform)

        with col3:
            st.metric("Objective", objective)

        st.subheader("💰 Business KPIs")

        impressions = number(get_value(campaign, "impressions"))
        clicks = number(get_value(campaign, "clicks"))
        conversions = number(get_value(campaign, "conversions"))

        spend = number(
            get_value(
                campaign,
                "ad_spend",
                "spend",
            )
        )

        revenue = number(get_value(campaign, "revenue"))
        profit = number(get_value(campaign, "profit"))

        cols = st.columns(6)

        cols[0].metric("Impressions", f"{impressions:,.0f}")
        cols[1].metric("Clicks", f"{clicks:,.0f}")
        cols[2].metric("Conversions", f"{conversions:,.0f}")
        cols[3].metric("Spend", f"${spend:,.2f}")
        cols[4].metric("Revenue", f"${revenue:,.2f}")
        cols[5].metric("Profit", f"${profit:,.2f}")

        st.subheader("📈 Performance Metrics")

        ctr = number(get_value(campaign, "CTR", "ctr"))
        cpc = number(get_value(campaign, "CPC", "cpc"))
        cpa = number(get_value(campaign, "CPA", "cpa"))
        roas = number(get_value(campaign, "ROAS", "roas"))

        conversion_rate = number(
            get_value(campaign, "conversion_rate")
        )

        bounce_rate = number(
            get_value(campaign, "bounce_rate")
        )

        cols = st.columns(6)

        cols[0].metric("CTR", f"{ctr:.2f}%")
        cols[1].metric("CPC", f"${cpc:,.2f}")
        cols[2].metric("CPA", f"${cpa:,.2f}")
        cols[3].metric("ROAS", f"{roas:.2f}x")
        cols[4].metric("Conversion Rate", f"{conversion_rate:.2f}%")
        cols[5].metric("Bounce Rate", f"{bounce_rate:.2f}%")

        st.subheader("🔎 Anomaly Detection")

        anomaly = result.get("anomaly_detected", False)
        reasons = result.get("anomaly_reasons", "")

        if anomaly:
            st.error(f"🚨 Anomaly Detected\n\n{reasons}")
        else:
            st.success("✅ No significant anomaly detected.")

        st.subheader("🎯 Campaign Prioritization")

        priority = str(
            result.get("priority", "N/A")
        ).upper()

        score = number(
            result.get("priority_score", 0)
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Priority Score", f"{score:.2f}")

        with col2:
            if priority == "CRITICAL":
                st.error(f"🚨 {priority}")
            elif priority == "HIGH":
                st.warning(f"⚠️ {priority}")
            elif priority == "MEDIUM":
                st.info(f"🟡 {priority}")
            else:
                st.success(f"🟢 {priority}")

        st.subheader("🧠 AI Performance Analysis")

        analysis = result.get("performance_analysis", "")

        if analysis:
            st.markdown(
                '<div class="ai-card">',
                unsafe_allow_html=True,
            )
            st.markdown(analysis)
            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("No performance analysis available.")

        st.subheader("🔬 AI Root Cause Analysis")

        root_cause = result.get("root_cause", "")

        if root_cause:
            st.markdown(
                '<div class="ai-card">',
                unsafe_allow_html=True,
            )
            st.markdown(root_cause)
            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("No root-cause analysis available.")

        st.subheader("💡 AI Recommendation")

        recommendation = result.get("recommendation", "")

        if recommendation:
            st.markdown(
                '<div class="ai-card">',
                unsafe_allow_html=True,
            )
            st.markdown(recommendation)
            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("No recommendation available.")

        st.subheader("👤 Human Approval")

        st.info(
            "Review the AI recommendation before "
            "approving or rejecting it."
        )

        current_decision = st.session_state.get(
            "human_decision",
            "PENDING",
        )

        if current_decision == "PENDING":
            col1, col2 = st.columns(2)

            with col1:
                approve = st.button(
                    "✅ Approve Recommendation",
                    use_container_width=True,
                )

            with col2:
                reject = st.button(
                    "❌ Reject Recommendation",
                    use_container_width=True,
                )

            if approve:
                try:
                    audit_result = save_audit(
                        {
                            **result,
                            "human_approval": "APPROVED",
                        }
                    )

                    st.session_state["human_decision"] = "APPROVED"
                    st.session_state["audit_status"] = audit_result.get(
                        "audit_status",
                        "SAVED",
                    )

                    st.success(
                        "✅ Recommendation approved "
                        "and audit trail saved."
                    )

                    st.rerun()

                except Exception as e:
                    st.error("❌ Approval failed.")
                    st.exception(e)

            if reject:
                try:
                    audit_result = save_audit(
                        {
                            **result,
                            "human_approval": "REJECTED",
                        }
                    )

                    st.session_state["human_decision"] = "REJECTED"
                    st.session_state["audit_status"] = audit_result.get(
                        "audit_status",
                        "SAVED",
                    )

                    st.warning(
                        "❌ Recommendation rejected "
                        "and audit trail saved."
                    )

                    st.rerun()

                except Exception as e:
                    st.error("❌ Rejection failed.")
                    st.exception(e)

        else:
            if current_decision == "APPROVED":
                st.success("✅ Recommendation Approved")
            elif current_decision == "REJECTED":
                st.error("❌ Recommendation Rejected")

        st.subheader("📋 Audit Trail")

        human_decision = st.session_state.get(
            "human_decision",
            "PENDING",
        )

        audit_status = st.session_state.get(
            "audit_status",
            "NOT SAVED",
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Human Decision", human_decision)

        with col2:
            st.metric("Audit Status", audit_status)


elif page == "Performance Overview":
    st.header("📈 Performance Overview")

    db_path = get_database_path()
    table = get_campaign_table()

    if not db_path:
        st.error("Marketing database not found.")

    elif not table:
        st.error("Campaign table not found.")

    else:
        conn = sqlite3.connect(db_path)

        df = pd.read_sql_query(
            f"SELECT * FROM [{table}]",
            conn,
        )

        conn.close()

        st.write(f"Total Campaigns: **{len(df):,}**")

        st.dataframe(
            df,
            use_container_width=True,
            height=550,
        )


else:
    st.header("🤖 About AI Marketing Performance Agent")

    st.write(
        """
        This AI agent analyzes marketing campaigns and identifies
        performance problems automatically.
        """
    )

    st.markdown("### Capabilities")

    st.write("✅ Campaign Performance Analysis")
    st.write("✅ Anomaly Detection")
    st.write("✅ Campaign Prioritization")
    st.write("✅ AI Root Cause Analysis")
    st.write("✅ AI Recommendations")
    st.write("✅ Human-in-the-Loop Approval")
    st.write("✅ Audit Trail")

    st.markdown("### Technology")

    st.write(
        "Python · LangGraph · LangChain · Gemini · "
        "SQLite · Pandas · Streamlit"
    )


st.divider()

st.caption(
    "AI Marketing Performance Agent · "
    "Built with LangGraph + Streamlit"
)

