import os
from dotenv import load_dotenv

load_dotenv()  # load all .env variables

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
API_KEY = os.getenv("YOUTUBE_API_KEY")


from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests

# Scopes needed for YouTube captions
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Step 1: Set up OAuth flow using env vars
flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    SCOPES
)

creds = flow.run_local_server(port=8000)
youtube = build("youtube", "v3", credentials=creds)

video_id = "hSO4zjeQO48"  # replace with your video ID

# List caption tracks
caption_response = youtube.captions().list(
    part="id,snippet",
    videoId=video_id
).execute()

items = caption_response.get("items", [])
if not items:
    print("No captions available for this video.")
else:
    # Pick the first track
    caption_id = items[0]["id"]
    track_kind = items[0]["snippet"]["trackKind"]
    
    if track_kind == "ASR":
        print("This is an auto-generated caption. Cannot download via API.")
    else:
        # Download via requests with OAuth token
        download_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}?tfmt=srt"
        headers = {"Authorization": f"Bearer {creds.token}"}
        r = requests.get(download_url, headers=headers)
        
        if r.status_code == 200:
            with open("captions.srt", "w", encoding="utf-8") as f:
                f.write(r.text)
            print("Captions saved as captions.srt")
        else:
            print("Error downloading captions:", r.status_code, r.text)
