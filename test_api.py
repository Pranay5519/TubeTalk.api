import os
import redis
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")

try:
    client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)
    if client.ping():
        print("✅ Redis URL is working!")
except redis.ConnectionError as e:
    print("❌ Redis connection failed:", e)
