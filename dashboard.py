import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Tesla News Sentiment Tracker", layout="wide")
st.title("Tesla (TSLA) News Sentiment Tracker")

DB_PATH = "news.db"

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

if st.button("Refresh news data"):
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
