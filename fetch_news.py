import feedparser

RSS_URL = "https://finance.yahoo.com/rss/headline?s=TSLA"

def fetch_articles():
    feed = feedparser.parse(RSS_URL)
    articles = []
    for entry in feed.entries:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", "unknown")
        })
    return articles

if __name__ == "__main__":
    articles = fetch_articles()
    print(f"Fetched {len(articles)} articles\n")
    for a in articles:
        print(f"- {a['title']} ({a['published']})")
