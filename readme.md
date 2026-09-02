# 📊 AI Marketing Performance Agent

An AI-powered marketing analytics application that helps identify underperforming campaigns, understand what is going wrong, and generate actionable recommendations.

The project combines traditional marketing KPIs with an AI agent workflow so that campaign analysis is not limited to just showing numbers.

## What does it do?

A marketing team may have hundreds of campaigns running across different platforms. Looking at every campaign manually can make it difficult to quickly identify which campaigns need attention.

This project automates that first level of analysis.

For a selected campaign, the system:

* Loads campaign data from SQLite
* Checks important marketing KPIs
* Detects potential performance anomalies
* Calculates a campaign priority score
* Uses Gemini to analyze campaign performance
* Identifies possible root causes
* Generates optimization recommendations
* Sends the recommendation through a human approval step
* Stores the final decision in an audit table

---

## 🔄 Agent Workflow

```text
Campaign Data
     ↓
Anomaly Detection
     ↓
Campaign Prioritization
     ↓
AI Performance Analysis
     ↓
Root Cause Analysis
     ↓
AI Recommendation
     ↓
Human Approval
     ↓
Audit Trail
```

The workflow is implemented using LangGraph, with each stage handled as a separate node.

---

## 🧠 Key Features

### Campaign Analysis

The application displays important campaign information including:

* Impressions
* Clicks
* Conversions
* Ad Spend
* Revenue
* Profit
* CTR
* CPC
* CPA
* ROAS
* Conversion Rate
* Bounce Rate

### Anomaly Detection

The agent checks campaign metrics against predefined business rules.

Examples include:

* Negative profit
* ROAS below 1
* Low conversion rate
* High CPA

This provides a simple rule-based layer before the AI analysis begins.

### Campaign Prioritization

Campaigns receive a priority score based on multiple performance signals.

The current scoring considers:

* Loss
* ROAS risk
* CPA risk
* Conversion risk

The campaign is then categorized as:

```text
CRITICAL
HIGH
MEDIUM
LOW
```

This helps focus attention on campaigns that potentially need action first.

### AI Performance Analysis

Gemini analyzes the campaign data and produces a structured performance review covering:

* Overall performance
* Strong signals
* Weak signals
* Most important business problem

The model is instructed to work only with the available campaign data instead of inventing missing metrics.

### Root Cause Analysis

The agent goes one step further than simply identifying a poor KPI.

It asks the LLM to determine:

* Primary root cause
* Supporting evidence
* Secondary contributing factors
* Confidence in the conclusion

### AI Recommendations

Based on the campaign analysis and root cause, the agent generates practical optimization actions.

Recommendations can include:

* Immediate actions
* Experiments to run
* Metrics to monitor

### Human-in-the-Loop

AI recommendations are not automatically treated as final decisions.

The Streamlit interface allows a user to:

* Approve the recommendation
* Reject the recommendation

The selected decision is then stored in the audit trail.

### Audit Trail

Approved and rejected recommendations are saved in SQLite along with campaign information and the AI-generated analysis.

This provides a basic record of what the system recommended and what decision was eventually made.

---

## 🏗️ Architecture

```text
                 ┌───────────────────┐
                 │   SQLite Database  │
                 └─────────┬─────────┘
                           │
                           ↓
                 ┌───────────────────┐
                 │   Load Campaign   │
                 └─────────┬─────────┘
                           │
                           ↓
                 ┌───────────────────┐
                 │ Anomaly Detection │
                 └─────────┬─────────┘
                           │
                           ↓
                 ┌───────────────────┐
                 │   Prioritization  │
                 └─────────┬─────────┘
                           │
                           ↓
                 ┌───────────────────┐
                 │ Gemini AI Analysis│
                 └─────────┬─────────┘
                           │
                           ↓
                 ┌───────────────────┐
                 │   Root Cause      │
                 └─────────┬─────────┘
                           │
                           ↓
                 ┌───────────────────┐
                 │  Recommendation   │
                 └─────────┬─────────┘
                           │
                           ↓
                 ┌───────────────────┐
                 │  Human Approval   │
                 └─────────┬─────────┘
                           │
                           ↓
                 ┌───────────────────┐
                 │   Audit History   │
                 └───────────────────┘
```

---

## 🛠️ Tech Stack

**Language**

* Python

**AI / LLM**

* Google Gemini
* LangChain

**Agent Workflow**

* LangGraph

**Data**

* Pandas
* SQLite

**Application**

* Streamlit

**Other**

* python-dotenv

---

## 📁 Project Structure

```text
AI-Marketing-Performance-Agent/
│
├── app.py
├── README.md
├── requirements.txt
│
├── data/
│   └── marketing.db
│
└── src/
    └── agent.py
```

---

## ⚙️ How It Works

### 1. Campaign Selection

The user selects a campaign from the available campaigns stored in SQLite.

### 2. Data Loading

The agent loads the campaign record and passes the data through the LangGraph workflow.

### 3. Rule-Based Checks

The system checks important metrics and determines whether the campaign shows any obvious performance problems.

### 4. Priority Calculation

A weighted score is calculated using multiple risk signals.

### 5. AI Analysis

Gemini receives the campaign data and analyzes its overall performance.

### 6. Root Cause

The AI looks for the most likely reason behind the campaign's poor performance.

### 7. Recommendation

The agent generates actions that could potentially improve the campaign.

### 8. Human Review

The recommendation is shown to the user before any final decision is recorded.

### 9. Audit

The approval or rejection decision is saved to SQLite.

---

## 💻 Running the Project Locally

Clone the repository:

```bash
git clone <your-repository-url>
cd AI-Marketing-Performance-Agent
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
```

Run the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 🔐 Environment Variables

The application requires a Google Gemini API key.

```env
GOOGLE_API_KEY=your_google_api_key
```

Do not commit the `.env` file or API keys to GitHub.

---

## 📊 Example Use Case

Imagine a campaign with:

```text
Spend:        $1,200
Revenue:      $850
Profit:       -$350
ROAS:         0.71x
CPA:          $620
```

The rule-based layer can flag the campaign as problematic.

The agent then analyzes the available metrics and generates a root-cause assessment and possible actions.

A marketer can review the recommendation and either approve or reject it.

The final decision is recorded in the audit trail.

---

## 🎯 Why I Built This

I wanted to build something closer to a real business workflow instead of a standalone ML or chatbot project.

The main idea was to combine:

```text
Business Data
      +
Rule-Based Analysis
      +
LLM Reasoning
      +
Agent Workflow
      +
Human Review
      +
Auditability
```

This makes the project a practical example of how GenAI can be used alongside traditional data analysis for business decision support.

---

## 🚀 Possible Improvements

Some areas I would explore in a production version:

* Connect directly with Meta Ads / Google Ads APIs
* Add historical campaign comparisons
* Add campaign trend analysis
* Store detailed AI responses in the database
* Add user authentication
* Add scheduled campaign monitoring
* Add email/Slack alerts for critical campaigns
* Add experiment tracking
* Add automated KPI dashboards
* Add LangSmith-based tracing and evaluation

---

## ⚠️ Disclaimer

This is a portfolio project designed to demonstrate AI agent workflows and marketing analytics.

The recommendations generated by the AI should be reviewed by a human before being used for actual campaign decisions.

---

## 👨‍💻 Author

**Gaurang Varshney**

AI / Generative AI Engineer

Interested in building practical AI systems, LLM applications, agent workflows, and business automation solutions.

