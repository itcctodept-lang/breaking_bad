import os

articles = {
    "breaking_news.txt": """
    URGENT: Massive partial power outage in downtown metropolis.
    Thousands without electricity. Transit systems halted.
    Emergency crews dispatched. Cause unknown at this time.
    """,
    "company_announcement.txt": """
    We are pleased to announce our Q3 financial results.
    Revenue up 15%. New product line launching next month.
    All employees invited to town hall on Friday.
    """,
    "suspicious_report.txt": """
    CONFIDENTIAL: Internal memo regarding potential data breach.
    Need legal and IT security review immediately.
    Do not distribute externally.
    """,
    "opinion_piece.txt": """
    Why remote work is the future.
    A personal reflection on productivity and work-life balance.
    It's time for a change in how we perceive the office.
    """
}

def generate_mock_data():
    feed_dir = os.path.join("data", "feed")
    os.makedirs(feed_dir, exist_ok=True)
    
    for filename, content in articles.items():
        with open(os.path.join(feed_dir, filename), 'w') as f:
            f.write(content.strip())
    
    print(f"Generated {len(articles)} mock articles in {feed_dir}")

if __name__ == "__main__":
    generate_mock_data()
