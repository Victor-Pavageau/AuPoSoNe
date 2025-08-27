"""File management utilities."""

import os

from ..config.settings import settings


def get_file_path(game_name, clip_index, is_original=True):
    """Generate file path for video files."""
    subfolder = "Originals" if is_original else "Edited"
    return os.path.join(
        settings.ROOT_PATH,
        game_name,
        subfolder,
        f"{game_name}-{clip_index}{settings.VIDEO_FILE_EXTENSION}",
    )


def ensure_directory_exists(file_path):
    """Ensure the directory for a file path exists."""
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)


def remove_files(filename):
    for subfolder in ["Originals", "Edited"]:
        file_path = os.path.join(
            settings.ROOT_PATH, filename.split("-")[0], subfolder, filename
        )
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed file: {file_path}")
