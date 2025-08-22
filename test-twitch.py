import os
import subprocess
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_twitch_access_token():
    oauth_token_url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }

    response = requests.post(oauth_token_url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]


def get_game_id(game_name):
    twitch_api_endpoint = f"https://api.twitch.tv/helix/games?name={game_name}"
    access_token = get_twitch_access_token()
    headers = {"Client-ID": client_id, "Authorization": f"Bearer {access_token}"}

    response = requests.get(twitch_api_endpoint, headers=headers)
    response.raise_for_status()
    return response.json()["data"][0]["id"]


def get_clips(game_id, started_at, ended_at, clips_count):
    twitch_clips_api_url = "https://api.twitch.tv/helix/clips"
    access_token = get_twitch_access_token()
    headers = {"Client-ID": client_id, "Authorization": f"Bearer {access_token}"}

    params = {
        "game_id": game_id,
        "first": clips_count,
        "started_at": started_at,
        "ended_at": ended_at,
    }

    response = requests.get(twitch_clips_api_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["data"]


def get_iso_formatted_datetime(dt):
    return dt.isoformat("T") + "Z"


def get_video_source_attribute(clip_url):
    video_tag = get_video_markup(clip_url)
    return get_src_attribute(video_tag)


def get_video_markup(video_url):
    selenium_web_driver.get(video_url)
    researched_tag = "video"
    WebDriverWait(selenium_web_driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, researched_tag)),
    )

    soup = BeautifulSoup(selenium_web_driver.page_source, "html.parser")

    return soup.find(researched_tag)


def get_src_attribute(video_tag):
    if video_tag.has_attr("src"):
        return video_tag["src"]
    return None


def download_video(video_url, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    response = requests.get(video_url, stream=True)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def get_file_path(game_name, clip_index, isOriginal):
    subfolder = "Originals" if isOriginal else "Edited"
    return os.path.join(
        ROOT_PATH,
        game_name,
        subfolder,
        f"{game_name}-{clip_index}{VIDEO_FILE_EXTENSION}",
    )


def crop_video(input_file_path, output_file_path):
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_file_path,
                "-lavfi",
                "[0:v]crop=ih*4/3:ih:(iw-ih*4/3)/2:0,scale=1080:-1[cropped];[cropped]scale=-1:1920,boxblur=luma_radius=min(h\\,w)/40:luma_power=3:chroma_radius=min(cw\\,ch)/40:chroma_power=1[bg];[bg][cropped]overlay=(W-w)/2:(H-h)/2,setsar=1,crop=w=1080:h=1920",
                output_file_path,
            ],
            check=True,
        )
        os.remove(input_file_path)
    except subprocess.CalledProcessError:
        print(f"Failed converting the video {input_file_path}")


# Twitch API credentials

load_dotenv()

client_id = os.getenv("TWITCH_CLIENT_ID")
client_secret = os.getenv("TWITCH_CLIENT_SECRET")

# Configure Selenium WebDriver
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

selenium_web_driver = webdriver.Chrome(options=options)

ROOT_PATH = "C:/Users/Victor/Downloads/test/"
VIDEO_FILE_EXTENSION = ".mp4"
CLIPS_COUNT = 24

game_name = "Valorant"
game_id = get_game_id(game_name)

now = datetime.now()
yesterday = now - timedelta(hours=24)

clips = get_clips(
    game_id,
    get_iso_formatted_datetime(yesterday),
    get_iso_formatted_datetime(now),
    CLIPS_COUNT,
)

try:
    for i in range(len(clips)):
        print(f"Processing clip {i + 1}/{len(clips)}: {clips[i]['url']}")
        video_source_url = get_video_source_attribute(clips[i]["url"])
        print(f"Video source URL: {video_source_url}")
        original_video_path = get_file_path(game_name, i, True)
        download_video(video_source_url, original_video_path)
        print(f"Downloaded video to: {original_video_path}")

        edited_video_path = get_file_path(game_name, i, False)
        crop_video(original_video_path, edited_video_path)
        print(f"Cropped video saved to: {edited_video_path}")

finally:
    selenium_web_driver.quit()
