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

    st.divider()
    st.subheader("Sentiment vs. Tesla Stock Price")

    import yfinance as yf

    try:
        price_data = yf.download("TSLA", period="1mo", interval="1d", progress=False)
        price_data = price_data.reset_index()

        # Flatten multi-level columns if present (newer yfinance versions do this)
        if isinstance(price_data.columns, pd.MultiIndex):
            price_data.columns = [c[0] for c in price_data.columns]

        price_data["Date"] = pd.to_datetime(price_data["Date"]).dt.date

        df["date_only"] = df["published"].dt.date
        daily_sentiment = df.groupby("date_only")["sentiment_score"].mean().reset_index()
        daily_sentiment.columns = ["Date", "avg_sentiment"]

        merged = pd.merge(price_data[["Date", "Close"]], daily_sentiment, on="Date", how="inner")

        if len(merged) >= 2:
            correlation = merged["Close"].corr(merged["avg_sentiment"])
            st.metric("Correlation (price vs. sentiment)", f"{correlation:.2f}")

            fig_corr = px.scatter(merged, x="avg_sentiment", y="Close",
                                   title="Daily Avg Sentiment vs. Closing Price",
                                   labels={"avg_sentiment": "Average Sentiment Score", "Close": "TSLA Close Price"})
            st.plotly_chart(fig_corr, use_container_width=True)

            st.caption(
                "Correlation ranges from -1 to 1. Values near 0 suggest little to no linear relationship "
                "between daily sentiment and price on the days observed. This is expected over a short "
                "window and should not be read as predictive."
            )
        else:
            st.info("Not enough overlapping days between news data and price data yet to compute correlation.")
    except Exception as e:
        st.warning(f"Could not load price comparison: {e}")
