"""Twitch API service for fetching clips and game information."""

from datetime import datetime, timedelta

import requests

from config.settings import settings


class TwitchService:
    """Service for interacting with Twitch API."""

    def __init__(self):
        self.client_id = settings.TWITCH_CLIENT_ID
        self.client_secret = settings.TWITCH_CLIENT_SECRET
        self._access_token = None

    def get_access_token(self):
        """Get OAuth access token for Twitch API."""
        oauth_token_url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        response = requests.post(oauth_token_url, params=params)
        response.raise_for_status()
        self._access_token = response.json()["access_token"]
        return self._access_token

    def _get_headers(self):
        """Get headers with authorization for API requests."""
        if not self._access_token:
            self.get_access_token()

        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self._access_token}",
        }

    def get_game_id(self, game_name):
        """Get game ID by game name."""
        twitch_api_endpoint = f"https://api.twitch.tv/helix/games?name={game_name}"
        headers = self._get_headers()

        response = requests.get(twitch_api_endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()["data"]

        if not data:
            raise ValueError(f"Game '{game_name}' not found")

        return data[0]["id"]

    def get_clips(self, game_id, started_at, ended_at, clips_count):
        """Get clips for a specific game within a time range."""
        twitch_clips_api_url = "https://api.twitch.tv/helix/clips"
        headers = self._get_headers()

        params = {
            "game_id": game_id,
            "first": clips_count,
            "started_at": started_at,
            "ended_at": ended_at,
        }

        response = requests.get(twitch_clips_api_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()["data"]

    def get_clips_for_last_24h(self, game_name, clips_count=1):
        """Get clips for a game from the last 24 hours."""
        game_id = self.get_game_id(game_name)

        now = datetime.now()
        yesterday = now - timedelta(hours=24)

        started_at = self._get_iso_formatted_datetime(yesterday)
        ended_at = self._get_iso_formatted_datetime(now)

        return self.get_clips(game_id, started_at, ended_at, clips_count)

    @staticmethod
    def _get_iso_formatted_datetime(dt):
        """Convert datetime to ISO format."""
        return dt.isoformat("T") + "Z"
