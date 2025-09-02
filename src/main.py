"""Main orchestrator for the AuPoSoNe application."""

import os

from config.settings import settings
from services.dropbox_service import DropboxService
from services.facebook_service import FacebookService
from services.instagram_service import InstagramService
from services.twitch_service import TwitchService
from services.video_service import VideoService
from utils.file_utils import get_file_path, remove_files
from utils.web_scraper import WebScraper


class AuPoSoNeOrchestrator:
    """Main orchestrator that coordinates all services."""

    def __init__(self):
        self.twitch_service = TwitchService()
        self.video_service = VideoService()
        self.dropbox_service = DropboxService()
        self.instagram_service = InstagramService()
        self.facebook_service = FacebookService()

    def process_clips(self, game_name="Valorant", clips_count=None):
        """
        Main method to process clips from Twitch to Instagram.

        Args:
            game_name: Name of the game to fetch clips for
            clips_count: Number of clips to process (default from settings)
        """
        if clips_count is None:
            clips_count = settings.CLIPS_COUNT

        print(f"Starting clip processing for {game_name}...")

        # Fetch clips from Twitch
        clips = self.twitch_service.get_clips_for_last_24h(game_name, clips_count)

        if not clips:
            print(f"No clips found for {game_name}")
            return

        print(f"Found {len(clips)} clips to process")

        processed_files = []

        # Process each clip
        with WebScraper() as scraper:
            for i, clip in enumerate(clips):
                try:
                    processed_file = self._process_single_clip(
                        scraper, clip, game_name, i
                    )
                    if processed_file:
                        processed_files.append(processed_file)
                except Exception as e:
                    print(f"Error processing clip {i + 1}: {e}")
                    continue

        # Upload and publish processed files
        for filepath in processed_files:
            try:
                self._upload_and_publish(filepath)
                self._remove_processed_files(filepath, game_name)
            except Exception as e:
                print(f"Error uploading/publishing {filepath}: {e}")
                raise e

    def _process_single_clip(self, scraper, clip, game_name, clip_index):
        """Process a single clip: download and crop."""
        print(f"Processing clip {clip_index + 1}: {clip['url']}")

        # Extract video source URL
        video_source_url = scraper.get_video_source_url(clip["url"])
        if not video_source_url:
            print(f"Could not extract video source from {clip['url']}")
            return None

        print(f"Video source URL: {video_source_url}")

        # Download original video
        original_video_path = get_file_path(game_name, clip_index, is_original=True)
        self.video_service.download_video(video_source_url, original_video_path)

        # Process video editing
        edited_video_path = get_file_path(game_name, clip_index, is_original=False)
        self.video_service.crop_video_for_reels(original_video_path, edited_video_path)

        return edited_video_path

    def _upload_and_publish(self, filepath):
        """Upload file to Dropbox and publish to Instagram."""
        # Upload to Dropbox
        download_url = self.dropbox_service.upload_file(filepath)
        print(f"Successfully uploaded to: {download_url}")

        # Publish with retry logic
        self.instagram_service.publish_with_retry(download_url)
        self.facebook_service.publish_video(download_url)

    def _remove_processed_files(self, filepath, game_name):
        """Remove processed files from local and shared storages."""
        remove_files(os.path.basename(filepath))
        self.dropbox_service.delete_game_folder(game_name)
