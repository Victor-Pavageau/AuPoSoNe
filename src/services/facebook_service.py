"""Facebook service for publishing reels."""

import requests

from config.settings import settings


class FacebookService:
    """Service for publishing content to Facebook."""

    def __init__(self):
        self.access_token = settings.FACEBOOK_PAGE_ACCESS_TOKEN
        self.root_url = settings.facebook_root_url

    def publish_video(self, video_url):
        """
        Publish a video.

        Args:
            video_url: The URL of the video to publish

        Returns:
            dict: Publication response if successful

        Raises:
            Exception: If publication fails after max_wait_time
        """

        url = f"{self.root_url}/videos"
        payload = {
            "file_url": video_url,
            "access_token": self.access_token,
            # title: 'Title',
            # description: 'Description',
        }

        response = requests.post(url, data=payload)
        response.raise_for_status()

        post_id = response.json().get("id")
        if not post_id:
            raise Exception("Failed to publish the video on the Facebook page")

        print(f"Published video on Facebook page: {post_id}")
        return post_id
