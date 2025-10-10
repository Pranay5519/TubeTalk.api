import os
import redis
import pickle
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read Redis URL (example: redis://default:password@redis:6379/0)
REDIS_URL = os.getenv("REDIS_URL")

try:
    # Create Redis client using URL
    redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=False)
    redis_client.ping()
    logging.info("✅ Connected to Redis successfully")
except redis.ConnectionError:
    logging.error("❌ Redis connection failed. Check REDIS_URL or server status.")
    redis_client = None


def get_cache(key: str):
    """Retrieve cached value for a given key."""
    if not redis_client:
        return None
    data = redis_client.get(key)
    return pickle.loads(data) if data else None


def set_cache(key: str, value, ttl: int = 7200):
    """Set a value in Redis cache with a TTL, but skip if Redis memory is full."""
    if not redis_client:
        return

    try:
        # Get Redis memory usage info
        info = redis_client.info(section="memory")
        used_memory = info.get("used_memory", 0)
        max_memory = info.get("maxmemory", 0)

        # If maxmemory is set and used memory is above 95%, skip caching
        if max_memory > 0 and used_memory / max_memory > 0.95:
            logging.warning("⚠️ Redis memory nearly full. Skipping cache write.")
            return

        # Safe to cache
        redis_client.set(key, pickle.dumps(value), ex=ttl)

    except redis.RedisError as e:
        logging.error(f"❌ Redis error: {e}")
