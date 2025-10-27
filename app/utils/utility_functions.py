from youtube_transcript_api import YouTubeTranscriptApi
import re
from youtube_transcript_api.proxies import WebshareProxyConfig
"""def load_transcript(url: str) -> str | None:
 
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    if match:
        video_id = match.group(1)
        try:
            captions = YouTubeTranscriptApi().fetch(video_id,languages=['en','hi']).snippets
            data = [f"{item.text} ({item.start})" for item in captions]
            return " ".join(data)
        except Exception as e:
            print(f"❌ Error fetching transcript: {e}")
            return None
"""        
def load_transcript(url : str) -> str | None:
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    if match:
        video_id = match.group(1)
        try:
            captions = YouTubeTranscriptApi( proxy_config=WebshareProxyConfig(
        proxy_username="uovoumor",
        proxy_password="udk28jufv40l",
    )).fetch(video_id,languages=['en','hi']).snippets
            data = [f"{item.text} ({item.start})" for item in captions]
            return " ".join(data)
        except Exception as e:
            print(f"❌ Error fetching transcript: {e}")
            return None
    else:
        print("❌ Invalid YouTube URL")
        return None