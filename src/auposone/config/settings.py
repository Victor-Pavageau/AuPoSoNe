"""Configuration settings for the application."""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Twitch API Configuration
    TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
    TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

    # Instagram API Configuration
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")
    INSTAGRAM_BASE_URL = "https://graph.facebook.com/v23.0"

    # Dropbox Configuration
    DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

    # Video Processing Configuration
    ROOT_PATH = os.path.join(os.getcwd(), "clips")
    VIDEO_FILE_EXTENSION = ".mp4"
    CLIPS_COUNT = 1

    # Chrome WebDriver Configuration
    CHROME_OPTIONS = [
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ]

    @property
    def instagram_root_url(self):
        """Get the Instagram API root URL."""
        return f"{self.INSTAGRAM_BASE_URL}/{self.INSTAGRAM_USER_ID}"

    def validate(self):
        """Validate that all required environment variables are set."""
        required_vars = [
            ("TWITCH_CLIENT_ID", self.TWITCH_CLIENT_ID),
            ("TWITCH_CLIENT_SECRET", self.TWITCH_CLIENT_SECRET),
            ("INSTAGRAM_ACCESS_TOKEN", self.INSTAGRAM_ACCESS_TOKEN),
            ("INSTAGRAM_USER_ID", self.INSTAGRAM_USER_ID),
            ("DROPBOX_ACCESS_TOKEN", self.DROPBOX_ACCESS_TOKEN),
        ]

        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )


# Global settings instance
settings = Settings()
