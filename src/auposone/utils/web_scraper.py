"""Web scraping utilities using Selenium."""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config.settings import settings


class WebScraper:
    """Web scraper for extracting video sources from Twitch clips."""

    def __init__(self):
        self.driver = None
        self._setup_driver()

    def _setup_driver(self):
        """Set up Chrome WebDriver with configured options."""
        options = Options()
        for option in settings.CHROME_OPTIONS:
            options.add_argument(option)

        self.driver = webdriver.Chrome(options=options)

    def get_video_source_url(self, clip_url):
        """Extract video source URL from a Twitch clip page."""
        try:
            video_tag = self._get_video_markup(clip_url)
            return self._get_src_attribute(video_tag)
        except Exception as e:
            print(f"Error extracting video source from {clip_url}: {e}")
            return None

    def _get_video_markup(self, video_url):
        """Get video markup from the page source."""
        self.driver.get(video_url)
        researched_tag = "video"

        # Wait for video element to be present
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, researched_tag)),
        )

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        return soup.find(researched_tag)

    @staticmethod
    def _get_src_attribute(video_tag):
        """Extract src attribute from video tag."""
        if video_tag and video_tag.has_attr("src"):
            return video_tag["src"]
        return None

    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
