
import os
import shutil
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ---------------- SETTINGS ----------------
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

SHORTS_FOLDER = "shorts"
UPLOADED_FOLDER = "uploaded"
LOG_FILE = "upload_log.txt"

# ---------------- AUTH ----------------
creds = None

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json",
            SCOPES
        )
        creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
        token.write(creds.to_json())

youtube = build("youtube", "v3", credentials=creds)

# ---------------- CREATE FOLDERS ----------------
os.makedirs(SHORTS_FOLDER, exist_ok=True)
os.makedirs(UPLOADED_FOLDER, exist_ok=True)

# ---------------- LOG FUNCTIONS ----------------
def load_uploaded_videos():
    if not os.path.exists(LOG_FILE):
        return set()

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file)


def save_uploaded_video(filename):
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(filename + "\n")


# ---------------- GET VIDEOS ----------------
uploaded_videos = load_uploaded_videos()

videos = sorted([
    f for f in os.listdir(SHORTS_FOLDER)
    if f.lower().endswith(".mp4")
    and f not in uploaded_videos
])

if not videos:
    print("No new videos found.")
    exit()

# ---------------- UPLOAD ALL VIDEOS ----------------
for filename in videos:

    video_path = os.path.join(SHORTS_FOLDER, filename)

    # ---------------- TITLE ----------------
    title = os.path.splitext(filename)[0]
    title = title.replace("_", " ")
    title = title.replace("-", " ")
    title = title.title()
    title += " ⚽ #shorts"

    # ---------------- DESCRIPTION ----------------
    description = """
⚽ Daily Football Shorts

🔥 Best Football Moments
🏆 Skills • Goals • Highlights

Subscribe for more football content!

#shorts
#football
#soccer
#footballshorts
#messi
#ronaldo
#goals
#viral
#ytshorts
"""

    # ---------------- REQUEST BODY ----------------
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [
                "football",
                "soccer",
                "football shorts",
                "messi",
                "ronaldo",
                "goals",
                "skills",
                "highlights",
                "viral",
                "ytshorts"
            ],
            "categoryId": "17"
        },
        "status": {
            "privacyStatus": "private"
        }
    }

    try:
        media_file = MediaFileUpload(video_path, resumable=True)

        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media_file
        )

        response = request.execute()

        print(f"\nUploaded: {filename}")
        print("Video ID:", response["id"])

        # Release file lock
        try:
            media_file.stream().close()
        except:
            pass

        time.sleep(2)

        # Move video
        destination = os.path.join(UPLOADED_FOLDER, filename)

        shutil.copy2(video_path, destination)
        os.remove(video_path)

        print(f"Moved {filename} to uploaded folder")

        # Update upload log
        save_uploaded_video(filename)

        print("Added to upload_log.txt")

    except Exception as e:
        print(f"Error uploading {filename}")
        print(e)

print("\nAll videos uploaded successfully!")
