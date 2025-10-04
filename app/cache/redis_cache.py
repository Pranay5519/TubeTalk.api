import redis
import pickle
import logging
import time

try:
    redis_client = redis.Redis(host="localhost", port=6379, db=0)
    redis_client.ping()
    logging.info("✅ Connected to Redis")
except redis.ConnectionError:
    logging.error("❌ Redis not running")
    redis_client = None

def get_cache(key: str):
    if not redis_client:
        return None
    data = redis_client.get(key)
    return pickle.loads(data) if data else None

def set_cache(key: str, value, ttl: int = 7200):
    if redis_client:
        redis_client.set(key, pickle.dumps(value), ex=ttl)
