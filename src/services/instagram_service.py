"""Instagram service for publishing reels."""

import time

import requests

from config.settings import settings


class InstagramService:
    """Service for publishing content to Instagram."""

    def __init__(self):
        self.access_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.root_url = settings.instagram_root_url

    def _create_container(self, video_url):
        """Create a media container for Instagram Reels."""
        url = f"{self.root_url}/media"
        payload = {
            "video_url": video_url,
            "media_type": "REELS",
            "access_token": self.access_token,
        }

        response = requests.post(url, data=payload)
        response.raise_for_status()

        container_id = response.json().get("id")
        if not container_id:
            raise Exception("Failed to create container")

        print(f"Container created: {container_id}")
        return container_id

    def _publish_container(self, container_id):
        """Publish a media container to Instagram."""
        url = f"{self.root_url}/media_publish"
        payload = {"creation_id": container_id, "access_token": self.access_token}

        response = requests.post(url, data=payload)
        response.raise_for_status()

        publish_response = response.json()
        print(f"Publication successful: {publish_response}")
        return publish_response

    def publish_with_retry(self, video_url, max_wait_time=600, retry_interval=60):
        """
        Create a container and publish it with retry logic.

        Args:
            video_url: The URL of the video to publish
            max_wait_time: Maximum time to wait in seconds (default: 10 minutes)
            retry_interval: Time between retries in seconds (default: 1 minute)

        Returns:
            dict: Publication response if successful

        Raises:
            Exception: If publication fails after max_wait_time
        """

        container_id = self._create_container(video_url)

        # Wait initial time before first attempt
        print(f"Waiting {retry_interval} seconds before publishing...")
        time.sleep(retry_interval)

        waited_time = retry_interval

        while waited_time < max_wait_time:
            try:
                publish_response = self._publish_container(container_id)
                print(f"Publication successful after {waited_time} seconds.")
                return publish_response

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 400:
                    print(
                        f"Error 400, waiting {retry_interval} seconds before retrying... "
                        f"({waited_time} seconds elapsed)"
                    )
                    try:
                        error_details = e.response.json()
                        print(f"Error details: {error_details}")
                    except Exception:
                        print(f"Error response: {e.response.text}")

                    time.sleep(retry_interval)
                    waited_time += retry_interval
                else:
                    print(f"Unexpected error: {e}")
                    raise

        raise Exception(f"Failed to publish after {max_wait_time} seconds of waiting.")
