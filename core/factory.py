from scrapers.youtube_scraper import YouTubeScraper
from scrapers.bluesky_scraper import BlueskyScraper

class ScraperFactory:
    """The Umpire: Decides which scraper to deploy based on the platform name."""
    
    _SCRAPERS = {
        "youtube": YouTubeScraper,
        "bluesky": BlueskyScraper
    }

    @classmethod
    def get_scraper(cls, platform: str):
        scraper_class = cls._SCRAPERS.get(platform.lower())
        if not scraper_class:
            raise ValueError(f"Platform '{platform}' is not supported yet.")
        return scraper_class()
