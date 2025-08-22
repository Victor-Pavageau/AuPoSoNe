import json
import os
import subprocess
import time
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()


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
    print(f"Cropping video: {input_file_path} to {output_file_path}")

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


ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
BASE_URL = "https://graph.facebook.com/v23.0"
IG_USER_ID = os.getenv("INSTAGRAM_USER_ID")
ROOT_URL = f"{BASE_URL}/{IG_USER_ID}"


def upload_file(filepath):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Fichier introuvable: {filepath}")

    filename = os.path.basename(filepath)
    path = f"/test/Valorant/{filename}"

    upload_url = "https://content.dropboxapi.com/2/files/upload"

    # Your API token
    token = os.getenv("DROPBOX_ACCESS_TOKEN")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": json.dumps(
            {
                "autorename": False,
                "mode": "add",
                "mute": False,
                "path": path,
                "strict_conflict": False,
            }
        ),
    }

    with open(filepath, "rb") as f:
        upload_response = requests.post(upload_url, headers=headers, data=f)

    if upload_response.status_code != 200:
        print(upload_response.status_code)
        print(upload_response.text)
        return None

    get_link_url = "https://api.dropboxapi.com/2/files/get_temporary_link"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = {"path": path}

    response = requests.post(get_link_url, headers=headers, data=json.dumps(data))

    return response.json().get("link", "")


def create_container(video_url):
    url = f"{ROOT_URL}/media"
    payload = {
        "video_url": video_url,
        "media_type": "REELS",
        "access_token": ACCESS_TOKEN,
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    container_id = response.json().get("id")
    print(f"Container créé : {container_id}")
    return container_id


def publish_container(container_id):
    url = f"{ROOT_URL}/media_publish"
    payload = {"creation_id": container_id, "access_token": ACCESS_TOKEN}
    response = requests.post(url, data=payload)
    response.raise_for_status()
    publish_response = response.json()
    print(f"Publication réussie : {publish_response}")
    return publish_response


# Exécution du script

# import sys
# if len(sys.argv) < 2:
#     print("Usage : python upload_transfer.py chemin/vers/fichier.mp4")
#     sys.exit(1)

# Twitch API credentials

client_id = os.getenv("TWITCH_CLIENT_ID")
client_secret = os.getenv("TWITCH_CLIENT_SECRET")

# Configure Selenium WebDriver
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

selenium_web_driver = webdriver.Chrome(options=options)

ROOT_PATH = os.path.join(os.getcwd(), "test")
VIDEO_FILE_EXTENSION = ".mp4"
CLIPS_COUNT = 1

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

files = []

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
        files.append(edited_video_path)

finally:
    selenium_web_driver.quit()

try:
    for filepath in files:
        download_url = upload_file(filepath)
        print(f"Successfully uploaded to: {download_url}")
        container_id = create_container(download_url)
except Exception as e:
    print(f"Error : {e}")

time.sleep(60)
waited_time = 60
publish_succeed = False

while waited_time < 600:  # 10 minutes
    try:
        publish_response = publish_container(container_id)
        publish_succeed = True
        break
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print(
                f"Error 400, waiting 1 minute before retrying... ({waited_time} seconds elapsed)"
            )
            print(e.response.json())
            time.sleep(60)
            waited_time += 60
        else:
            print(f"Unexpected error : {e}")
            break

if waited_time >= 600 and not publish_succeed:
    print("Failed to publish after 10 minutes of waiting.")
else:
    print(f"Publication successful after {waited_time} seconds.")
    print(f"Publication response : {publish_response}")
