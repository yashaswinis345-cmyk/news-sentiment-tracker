# Tesla (TSLA) News Sentiment Tracker

A real-time sentiment analysis tool that tracks news coverage of Tesla stock using FinBERT, a finance-specific NLP model, and visualizes sentiment trends through an interactive dashboard.

## What it does

- Fetches live Tesla-related news headlines via RSS
- Runs each headline through FinBERT to classify sentiment (positive/neutral/negative)
- Stores results in a local SQLite database
- Displays sentiment distribution and trends in an interactive Streamlit dashboard
- Can run on a schedule to continuously track sentiment over time

## Tech stack

- **Python** for the core pipeline
- **FinBERT** (Hugging Face `ProsusAI/finbert`) for finance-domain sentiment analysis
- **SQLite** for lightweight persistent storage
- **Streamlit + Plotly** for the interactive dashboard
- **APScheduler** for automated periodic fetching

## Project structure

- `fetch_news.py` — pulls live news headlines via RSS
- `analyze.py` — runs FinBERT sentiment analysis and stores results
- `dashboard.py` — Streamlit dashboard for visualizing sentiment data
- `scheduler.py` — automates fetching + analysis on a timer

## Running locally

```bash
pip install -r requirements.txt
python analyze.py       # fetch news + run sentiment analysis
streamlit run dashboard.py   # launch the dashboard
Then push it:
```bash
git add .
git commit -m "Add README"
git push

streamlit run yourscript.py
cd ~/news-sentiment-tracker
cat > dashboard.py << 'EOF'
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Tesla News Sentiment Tracker", layout="wide")
st.title("Tesla (TSLA) News Sentiment Tracker")

DB_PATH = "news.db"

# If the database doesn't exist yet, run the pipeline to create it
if not os.path.exists(DB_PATH):
    st.info("First-time setup: fetching news and running sentiment analysis. This may take a minute...")
    from analyze import analyze_and_store
    analyze_and_store()

conn = sqlite3.connect(DB_PATH)
try:
    df = pd.read_sql_query("SELECT * FROM articles", conn)
except Exception:
    df = pd.DataFrame()
conn.close()

st.button("🔄 Refresh news data")
if st.session_state.get("refresh_clicked"):
    from analyze import analyze_and_store
    analyze_and_store()
    st.rerun()

if df.empty:
    st.warning("No articles found yet. Click refresh above to fetch news.")
else:
    df["published"] = pd.to_datetime(df["published"], errors="coerce", utc=True)
    df = df.sort_values("published", ascending=False)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Articles", len(df))
    col2.metric("Positive", (df["sentiment_label"] == "positive").sum())
    col3.metric("Neutral", (df["sentiment_label"] == "neutral").sum())
    col4.metric("Negative", (df["sentiment_label"] == "negative").sum())

    st.divider()

    st.subheader("Sentiment Distribution")
    sentiment_counts = df["sentiment_label"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment", "count"]
    fig_pie = px.pie(sentiment_counts, names="sentiment", values="count",
                      color="sentiment",
                      color_discrete_map={"positive": "green", "neutral": "gray", "negative": "red"})
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Sentiment Score Over Time")
    df_sorted = df.sort_values("published")
    fig_line = px.line(df_sorted, x="published", y="sentiment_score", color="sentiment_label",
                        markers=True,
                        color_discrete_map={"positive": "green", "neutral": "gray", "negative": "red"})
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Latest Articles")
    display_df = df[["published", "title", "sentiment_label", "sentiment_score", "link"]]
    st.dataframe(display_df, use_container_width=True)
