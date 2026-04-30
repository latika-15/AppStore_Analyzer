import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ CONFIG ------------------
st.set_page_config(page_title="App Review Analyzer", layout="wide")

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/final_dataset.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    return df

df = load_data()

# ------------------ SIDEBAR FILTERS ------------------
st.sidebar.title("Filters")

apps = sorted(df["app"].dropna().unique().tolist())
sentiments = sorted(df["sentiment"].dropna().unique().tolist())

selected_apps = st.sidebar.multiselect("Select App", apps, default=apps)
selected_sentiments = st.sidebar.multiselect("Select Sentiment", sentiments, default=sentiments)

filtered = df[
    (df["app"].isin(selected_apps)) &
    (df["sentiment"].isin(selected_sentiments))
]

# ------------------ CSS (KPI CARDS) ------------------
st.markdown("""
<style>
.kpi {
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    padding: 18px;
    border-radius: 16px;
    color: white;
    text-align: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}
.kpi h2 { margin: 0; font-size: 30px; }
.kpi p { margin: 0; opacity: 0.85; }
</style>
"""
, unsafe_allow_html=True)

# ------------------ KPIs ------------------
total_reviews = len(filtered)
avg_rating = round(filtered["rating"].mean(), 2) if total_reviews else 0

positive_pct = round((filtered["sentiment"] == "Positive").mean() * 100, 2) if total_reviews else 0
negative_pct = round((filtered["sentiment"] == "Negative").mean() * 100, 2) if total_reviews else 0

feature_pct = round((filtered["feature_request"] == True).mean() * 100, 2) if total_reviews else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.markdown(f'<div class="kpi"><h2>{total_reviews}</h2><p>Total Reviews</p></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="kpi"><h2>{avg_rating}</h2><p>Avg Rating</p></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="kpi"><h2>{positive_pct}%</h2><p>Positive %</p></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="kpi"><h2>{negative_pct}%</h2><p>Negative %</p></div>', unsafe_allow_html=True)
k5.markdown(f'<div class="kpi"><h2>{feature_pct}%</h2><p>Feature Request %</p></div>', unsafe_allow_html=True)

st.title("App Review Insights Dashboard")

# ------------------ TABS ------------------
tab1, tab2, tab3 = st.tabs(["Overview", "Complaint Analysis", "Feature Insights"])

# ------------------ OVERVIEW ------------------
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        sentiment_counts = filtered["sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["sentiment", "count"]
        fig = px.pie(sentiment_counts, names="sentiment", values="count", hole=0.5, title="Sentiment Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        time_df = filtered.groupby("date").size().reset_index(name="count")
        fig2 = px.line(time_df, x="date", y="count", title="Reviews Over Time")
        st.plotly_chart(fig2, use_container_width=True)

    # Last 5 rows per app
    st.subheader("Last 5 Reviews per App")
    for app in apps:
        st.markdown(f"### {app}")
        st.dataframe(df[df["app"] == app].tail(5))

# ------------------ COMPLAINT ANALYSIS ------------------
with tab2:
    # Complaint = Negative sentiment (your fixed logic)
    comp_df = filtered[filtered["sentiment"] == "Negative"]

    c1, c2 = st.columns(2)

    with c1:
        issue_counts = comp_df["complaint_type"].value_counts().reset_index()
        issue_counts.columns = ["issue", "count"]
        fig3 = px.bar(issue_counts, x="issue", y="count", title="Top Issues")
        st.plotly_chart(fig3, use_container_width=True)

    with c2:
        app_issue = comp_df.groupby("app").size().reset_index(name="count")
        fig4 = px.bar(app_issue, x="app", y="count", title="App vs Issues")
        st.plotly_chart(fig4, use_container_width=True)

    trend = comp_df.groupby("date").size().reset_index(name="count")
    fig5 = px.line(trend, x="date", y="count", title="Issues Over Time")
    st.plotly_chart(fig5, use_container_width=True)

# ------------------ FEATURE INSIGHTS ------------------
with tab3:
    feat_df = filtered[filtered["feature_request"] == True]

    c1, c2 = st.columns(2)

    with c1:
        feat_app = feat_df.groupby("app").size().reset_index(name="count")
        fig6 = px.pie(feat_app, names="app", values="count", title="Feature Requests by App")
        st.plotly_chart(fig6, use_container_width=True)

    with c2:
        trend2 = feat_df.groupby("date").size().reset_index(name="count")
        fig7 = px.line(trend2, x="date", y="count", title="Feature Requests Trend")
        st.plotly_chart(fig7, use_container_width=True)

    # Keywords (simple)
    if "processed" in feat_df.columns:
        words = feat_df["processed"].str.split().explode()
        top_words = words.value_counts().head(10).reset_index()
        top_words.columns = ["word", "count"]

        fig8 = px.bar(top_words, x="word", y="count", title="Top Keywords")
        st.plotly_chart(fig8, use_container_width=True)


st.markdown("""
## 📌 Project Overview

This project is an **end-to-end App Review Analytics System** designed to transform raw user reviews into actionable insights for product improvement.

---

### 🎯 Objective
To analyze Play Store reviews and extract:
- User sentiment (Positive, Negative, Neutral)
- Key complaints (Bug, Performance, UI/UX, Network)
- Feature requests and user expectations
- Trends over time across multiple apps

---

### 🛠️ How It Was Built

#### 🔹 Data Collection
- Scraped real-world reviews using `google-play-scraper`
- Collected data for:
  - Instagram  
  - WhatsApp  
  - Snapchat  

#### 🔹 Data Processing
- Cleaned text (removed noise, links, symbols)
- Applied NLP preprocessing:
  - Tokenization
  - Lemmatization (using spaCy)

#### 🔹 Feature Engineering
- Sentiment analysis using TextBlob
- Complaint classification using rule-based NLP
- Feature request detection using keyword logic
- TF-IDF for extracting important words

#### 🔹 Analytics & Dashboard
- Built interactive dashboards in:
  - **Power BI** (for business insights)
  - **Streamlit** (for web deployment)

#### 🔹 Key KPIs Created
- Satisfaction Score (NPS-style)
- Complaint Rate (based on negative sentiment)
- Bug & Performance Issue %
- Feature Request %
- Top Keywords (user demand insights)

---

### 📊 Key Insights

- Majority of users are **satisfied**, but:
  - Bug and performance issues are dominant complaints  
- Significant number of users request new features  
- Feature demand is highest for certain apps (e.g., Instagram)  
- Keywords like *“update”, “add”, “fix”* highlight user expectations  

---

### 💡 Business Impact

This system helps:
- Identify critical product issues  
- Prioritize feature development  
- Improve user satisfaction  
- Support data-driven decision making  

---

### 🚀 Tech Stack

- **Python** (Pandas, NLP)
- **Streamlit** (Web App)
- **Power BI** (Dashboard)
- **Plotly** (Visualization)

---

### 👨‍💻 Final Outcome

An **end-to-end analytics solution** that converts unstructured user feedback into meaningful product insights and interactive dashboards.

---
""")