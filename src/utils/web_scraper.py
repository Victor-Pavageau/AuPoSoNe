"""Web scraping utilities using Selenium."""

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings


class WebScraper:
    """Web scraper for extracting video sources from Twitch clips."""

    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self._setup_driver()

    def _setup_driver(self):
        """Set up Chrome WebDriver with configured options."""
        options = Options()
        for option in settings.CHROME_OPTIONS:
            # Skip headless option if we want to run in visible mode
            if option == "--headless" and not self.headless:
                continue
            options.add_argument(option)

        # Add experimental options to avoid detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=options)

        # Execute script to remove webdriver property
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        # Set implicit wait
        self.driver.implicitly_wait(10)

    def get_video_source_url(self, clip_url):
        """Extract video source URL from a Twitch clip page."""
        try:
            return self._get_video_src(clip_url)
        except Exception:
            return None

    def _get_video_src(self, video_url):
        """Get video source URL from the page source."""
        self.driver.get(video_url)

        # Wait for page to load completely
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )

        # Scroll down to trigger any lazy loading
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        video_src = self._strategy_direct_video_src()

        if video_src:
            return video_src

        raise Exception("Video element not found or missing 'src' attribute")

    def _strategy_direct_video_src(self):
        """Strategy 1: Direct video tag with src attribute."""
        video_element = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        return video_element.get_attribute("src")

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
