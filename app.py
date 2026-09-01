import streamlit as st
import sys
from pathlib import Path
import sqlite3
import pandas as pd


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agent import app


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Marketing Performance Agent",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f7fb;
}

h1 {
    color: #111827;
}

h2 {
    color: #111827;
}

h3 {
    color: #374151;
}

div[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #e5e7eb;
    padding: 15px;
    border-radius: 12px;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

section[data-testid="stSidebar"] * {
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE
# ============================================================

def get_database_path():

    paths = [
        BASE_DIR / "data" / "marketing.db",
        BASE_DIR / "marketing.db",
        BASE_DIR / "src" / "marketing.db",
    ]

    for path in paths:

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
        WHERE type='table'
        """,
        conn
    )

    for table in tables["name"]:

        columns = pd.read_sql_query(
            f"PRAGMA table_info([{table}])",
            conn
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
        conn
    )

    conn.close()

    return df["campaign_id"].astype(str).tolist()


# ============================================================
# HELPERS
# ============================================================

def number(value):

    try:
        return float(value)

    except:
        return 0.0


def get_value(data, *keys, default=0):

    for key in keys:

        if key in data and data[key] is not None:
            return data[key]

    return default


# ============================================================
# SAVE HUMAN DECISION
# ============================================================

def save_human_decision(result, decision):

    db_path = get_database_path()

    if not db_path:
        raise FileNotFoundError(
            "Marketing database not found."
        )

    conn = sqlite3.connect(db_path)

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
            result["campaign_data"]["campaign_id"],
            result.get("priority", "N/A"),
            result.get("priority_score", 0),
            result.get("root_cause", ""),
            result.get("recommendation", ""),
            decision
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 Marketing AI")

    st.caption(
        "AI-powered campaign intelligence"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Campaign Analysis",
            "Performance Overview",
            "About Agent"
        ]
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


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 AI Marketing Performance Agent"
)

st.caption(
    "Autonomous campaign diagnostics, anomaly detection, "
    "root-cause analysis and AI-powered optimization."
)


# ============================================================
# CAMPAIGN ANALYSIS
# ============================================================

if page == "Campaign Analysis":

    st.header("🎯 Campaign Analysis")

    campaign_ids = get_campaign_ids()

    if campaign_ids:

        campaign_id = st.selectbox(
            "Select Campaign",
            campaign_ids
        )

    else:

        campaign_id = st.text_input(
            "Campaign ID",
            value="CAMP_09032"
        )

    analyze = st.button(
        "🚀 Analyze Campaign",
        type="primary",
        use_container_width=True
    )


    # ========================================================
    # RUN AGENT
    # ========================================================

    if analyze:

        if not campaign_id:

            st.error(
                "Please select a campaign."
            )

        else:

            with st.spinner(
                "🤖 AI Agent is analyzing campaign..."
            ):

                try:

                    result = app.invoke(
                        {
                            "campaign_id": campaign_id
                        }
                    )

                    st.session_state[
                        "result"
                    ] = result

                    st.session_state[
                        "campaign_id"
                    ] = campaign_id

                    st.session_state.pop(
                        "approval_result",
                        None
                    )

                    st.success(
                        "Campaign analysis completed."
                    )

                except Exception as e:

                    st.error(
                        "Agent execution failed."
                    )

                    st.exception(e)


    # ========================================================
    # SHOW RESULT
    # ========================================================

    if "result" in st.session_state:

        result = st.session_state["result"]

        campaign_id = st.session_state.get(
            "campaign_id",
            campaign_id
        )

        campaign = result.get(
            "campaign_data",
            {}
        )

        if not isinstance(campaign, dict):
            campaign = {}


        # ====================================================
        # CAMPAIGN INFO
        # ====================================================

        st.divider()

        st.subheader("Campaign Overview")

        platform = get_value(
            campaign,
            "platform",
            default="N/A"
        )

        objective = get_value(
            campaign,
            "campaign_objective",
            "objective",
            default="N/A"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Campaign ID",
                campaign_id
            )

        with col2:
            st.metric(
                "Platform",
                platform
            )

        with col3:
            st.metric(
                "Objective",
                objective
            )


        # ====================================================
        # BUSINESS KPIs
        # ====================================================

        st.subheader("💰 Business KPIs")

        impressions = number(
            get_value(
                campaign,
                "impressions"
            )
        )

        clicks = number(
            get_value(
                campaign,
                "clicks"
            )
        )

        conversions = number(
            get_value(
                campaign,
                "conversions"
            )
        )

        spend = number(
            get_value(
                campaign,
                "ad_spend",
                "spend"
            )
        )

        revenue = number(
            get_value(
                campaign,
                "revenue"
            )
        )

        profit = number(
            get_value(
                campaign,
                "profit"
            )
        )

        cols = st.columns(6)

        cols[0].metric(
            "Impressions",
            f"{impressions:,.0f}"
        )

        cols[1].metric(
            "Clicks",
            f"{clicks:,.0f}"
        )

        cols[2].metric(
            "Conversions",
            f"{conversions:,.0f}"
        )

        cols[3].metric(
            "Spend",
            f"${spend:,.2f}"
        )

        cols[4].metric(
            "Revenue",
            f"${revenue:,.2f}"
        )

        cols[5].metric(
            "Profit",
            f"${profit:,.2f}"
        )


        # ====================================================
        # PERFORMANCE
        # ====================================================

        st.subheader("📈 Performance Metrics")

        ctr = number(
            get_value(
                campaign,
                "CTR",
                "ctr"
            )
        )

        cpc = number(
            get_value(
                campaign,
                "CPC",
                "cpc"
            )
        )

        cpa = number(
            get_value(
                campaign,
                "CPA",
                "cpa"
            )
        )

        roas = number(
            get_value(
                campaign,
                "ROAS",
                "roas"
            )
        )

        conversion_rate = number(
            get_value(
                campaign,
                "conversion_rate"
            )
        )

        bounce_rate = number(
            get_value(
                campaign,
                "bounce_rate"
            )
        )

        cols = st.columns(6)

        cols[0].metric(
            "CTR",
            f"{ctr:.2f}%"
        )

        cols[1].metric(
            "CPC",
            f"${cpc:,.2f}"
        )

        cols[2].metric(
            "CPA",
            f"${cpa:,.2f}"
        )

        cols[3].metric(
            "ROAS",
            f"{roas:.2f}x"
        )

        cols[4].metric(
            "Conversion Rate",
            f"{conversion_rate:.2f}%"
        )

        cols[5].metric(
            "Bounce Rate",
            f"{bounce_rate:.2f}%"
        )


        # ====================================================
        # ANOMALY
        # ====================================================

        st.subheader("🔎 Anomaly Detection")

        anomaly = result.get(
            "anomaly_detected",
            False
        )

        reasons = result.get(
            "anomaly_reasons",
            ""
        )

        if anomaly:

            st.error(
                f"🚨 Anomaly Detected\n\n{reasons}"
            )

        else:

            st.success(
                "✅ No significant anomaly detected."
            )


        # ====================================================
        # PRIORITY
        # ====================================================

        st.subheader(
            "🎯 Campaign Prioritization"
        )

        priority = str(
            result.get(
                "priority",
                "N/A"
            )
        ).upper()

        score = number(
            result.get(
                "priority_score",
                0
            )
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Priority Score",
                f"{score:.2f}"
            )

        with col2:

            if priority == "CRITICAL":

                st.error(
                    f"🚨 {priority}"
                )

            elif priority == "HIGH":

                st.warning(
                    f"⚠️ {priority}"
                )

            elif priority == "MEDIUM":

                st.info(
                    f"🟡 {priority}"
                )

            else:

                st.success(
                    f"🟢 {priority}"
                )


        # ====================================================
        # AI ANALYSIS
        # ====================================================

        st.subheader(
            "🧠 AI Performance Analysis"
        )

        analysis = result.get(
            "performance_analysis",
            ""
        )

        if analysis:

            st.markdown(
                analysis
            )

        else:

            st.info(
                "No performance analysis available."
            )


        # ====================================================
        # ROOT CAUSE
        # ====================================================

        st.subheader(
            "🔬 AI Root Cause Analysis"
        )

        root_cause = result.get(
            "root_cause",
            ""
        )

        if root_cause:

            st.markdown(
                root_cause
            )

        else:

            st.info(
                "No root-cause analysis available."
            )


        # ====================================================
        # RECOMMENDATION
        # ====================================================

        st.subheader(
            "💡 AI Recommendation"
        )

        recommendation = result.get(
            "recommendation",
            ""
        )

        if recommendation:

            st.markdown(
                recommendation
            )

        else:

            st.info(
                "No recommendation available."
            )


        # ====================================================
        # HUMAN APPROVAL
        # ====================================================

        st.subheader(
            "👤 Human Approval"
        )

        approval_result = st.session_state.get(
            "approval_result"
        )

        if approval_result:

            decision = approval_result.get(
                "human_decision",
                "PENDING"
            )

            if decision == "APPROVED":

                st.success(
                    "✅ Recommendation approved."
                )

            elif decision == "REJECTED":

                st.warning(
                    "❌ Recommendation rejected."
                )

        else:

            st.info(
                "Review the AI recommendation before "
                "approving or rejecting it."
            )

            col1, col2 = st.columns(2)

            with col1:

                approve = st.button(
                    "✅ Approve Recommendation",
                    use_container_width=True
                )

            with col2:

                reject = st.button(
                    "❌ Reject Recommendation",
                    use_container_width=True
                )


            # =================================================
            # APPROVE
            # =================================================

            if approve:

                try:

                    save_human_decision(
                        result,
                        "APPROVED"
                    )

                    st.session_state[
                        "approval_result"
                    ] = {
                        "human_decision": "APPROVED",
                        "audit_status": "SAVED"
                    }

                    st.success(
                        "Recommendation approved and audit saved."
                    )

                except Exception as e:

                    st.error(
                        "Approval failed."
                    )

                    st.exception(e)


            # =================================================
            # REJECT
            # =================================================

            if reject:

                try:

                    save_human_decision(
                        result,
                        "REJECTED"
                    )

                    st.session_state[
                        "approval_result"
                    ] = {
                        "human_decision": "REJECTED",
                        "audit_status": "SAVED"
                    }

                    st.warning(
                        "Recommendation rejected and audit saved."
                    )

                except Exception as e:

                    st.error(
                        "Rejection failed."
                    )

                    st.exception(e)


        # ====================================================
        # AUDIT TRAIL
        # ====================================================

        st.subheader(
            "📋 Audit Trail"
        )

        approval_result = st.session_state.get(
            "approval_result",
            {}
        )

        human_decision = approval_result.get(
            "human_decision",
            "PENDING"
        )

        audit_status = approval_result.get(
            "audit_status",
            "NOT SAVED"
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Human Decision",
            human_decision
        )

        col2.metric(
            "Audit Status",
            audit_status
        )


# ============================================================
# PERFORMANCE OVERVIEW
# ============================================================

elif page == "Performance Overview":

    st.header(
        "📈 Performance Overview"
    )

    db_path = get_database_path()
    table = get_campaign_table()

    if not db_path:

        st.error(
            "Marketing database not found."
        )

    elif not table:

        st.error(
            "Campaign table not found."
        )

    else:

        conn = sqlite3.connect(
            db_path
        )

        df = pd.read_sql_query(
            f"SELECT * FROM [{table}]",
            conn
        )

        conn.close()

        st.write(
            f"Total Campaigns: **{len(df):,}**"
        )

        st.dataframe(
            df,
            use_container_width=True,
            height=550
        )


# ============================================================
# ABOUT
# ============================================================

else:

    st.header(
        "🤖 About AI Marketing Performance Agent"
    )

    st.write(
        """
        This AI agent analyzes marketing campaigns and identifies
        performance problems automatically.
        """
    )

    st.markdown(
        "### Capabilities"
    )

    st.write(
        "✅ Campaign Performance Analysis"
    )

    st.write(
        "✅ Anomaly Detection"
    )

    st.write(
        "✅ Campaign Prioritization"
    )

    st.write(
        "✅ AI Root Cause Analysis"
    )

    st.write(
        "✅ AI Recommendations"
    )

    st.write(
        "✅ Human-in-the-Loop Approval"
    )

    st.write(
        "✅ Audit Trail"
    )

    st.markdown(
        "### Technology"
    )

    st.write(
        "Python · LangGraph · LangChain · Gemini · SQLite · Pandas · Streamlit"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Marketing Performance Agent · "
    "Built with LangGraph + Streamlit"
)

