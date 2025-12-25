# app/scraper.py
import logging
from app.models import InvestmentOpportunity, db

logger = logging.getLogger(__name__)

def scrape_nse_kenya():
    try:
        import feedparser
        feed = feedparser.parse("https://www.nse.co.ke/news-announcements.rss")
        new_count = 0
        for entry in feed.entries:
            # Avoid duplicates
            if not InvestmentOpportunity.query.filter_by(url=entry.link).first():
                if any(kw in entry.title.lower() for kw in ['bond', 'ipo', 'offer', 'treasury']):
                    opp = InvestmentOpportunity(
                        title=entry.title,
                        source="NSE Kenya",
                        url=entry.link,
                        country="Kenya",
                        type="ipo" if "ipo" in entry.title.lower() else "bond"
                    )
                    db.session.add(opp)
                    new_count += 1
        db.session.commit()
        logger.info(f"Scraped {new_count} new opportunities from NSE.")
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        db.session.rollback()