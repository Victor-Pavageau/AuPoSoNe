"""Dropbox service for file upload and sharing."""

import json
import os

import requests

from ..config.settings import settings


class DropboxService:
    """Service for uploading files to Dropbox and getting temporary links."""

    def __init__(self):
        self.access_token = settings.DROPBOX_ACCESS_TOKEN

    def upload_file(self, filepath, remote_path=None):
        """Upload file to Dropbox and return a temporary link."""
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        filename = os.path.basename(filepath)

        # Use provided remote path or generate default one
        if remote_path is None:
            remote_path = f"/clips/Valorant/{filename}"

        # Upload the file
        upload_url = "https://content.dropboxapi.com/2/files/upload"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps(
                {
                    "autorename": False,
                    "mode": "add",
                    "mute": False,
                    "path": remote_path,
                    "strict_conflict": False,
                }
            ),
        }

        with open(filepath, "rb") as f:
            upload_response = requests.post(upload_url, headers=headers, data=f)

        if upload_response.status_code != 200:
            print(f"Upload failed with status {upload_response.status_code}")
            print(upload_response.text)
            raise Exception(f"Failed to upload file: {upload_response.text}")

        # Get temporary link
        return self._get_temporary_link(remote_path)

    def _get_temporary_link(self, remote_path):
        """Get a temporary download link for the uploaded file."""
        get_link_url = "https://api.dropboxapi.com/2/files/get_temporary_link"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        data = {"path": remote_path}

        response = requests.post(get_link_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        link = response.json().get("link", "")
        if not link:
            raise Exception("Failed to get temporary link from Dropbox")

        return link
