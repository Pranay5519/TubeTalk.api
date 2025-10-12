from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('PROXY_USERNAME')
password = os.getenv('PROXY_PASSWORD')

# ✅ Create the proxy config correctly (no host/port)
proxy_config = WebshareProxyConfig(
    proxy_username=username,
    proxy_password=password
)

# ✅ Create API object with the proxy config
ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)

# ✅ Fetch transcript
transcript = ytt_api.fetch("s3KnSb9b4Pk",languages = ['en','hi']).snippets
print(transcript)
