"""Video processing service for downloading and editing videos."""

import subprocess

import requests

from ..utils.file_utils import ensure_directory_exists


class VideoService:
    """Service for video download and processing operations."""

    libavfilters = {
        "fps": "[0:v]crop=ih*4/3:ih:(iw-ih*4/3)/2:0,scale=1080:-1[cropped];[cropped]scale=-1:1920,boxblur=luma_radius=min(h\\,w)/40:luma_power=3:chroma_radius=min(cw\\,ch)/40:chroma_power=1[bg];[bg][cropped]overlay=(W-w)/2:(H-h)/2,setsar=1,crop=w=1080:h=1920"
    }

    def download_video(self, video_url, output_path):
        """Download video from URL to specified path."""
        ensure_directory_exists(output_path)

        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Downloaded video to: {output_path}")

    def crop_video_for_reels(self, input_file_path, output_file_path):
        """Crop video to Instagram Reels format (9:16 aspect ratio)."""
        ensure_directory_exists(output_file_path)
        print(f"Cropping video: {input_file_path} to {output_file_path}")

        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    input_file_path,
                    "-lavfi",
                    self.libavfilters["fps"],
                    output_file_path,
                ],
                check=True,
            )
            print(f"Cropped video saved to: {output_file_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed converting the video {input_file_path}: {e}")
            raise
        except FileNotFoundError:
            print("FFmpeg not found. Please install FFmpeg and add it to your PATH.")
            raise
