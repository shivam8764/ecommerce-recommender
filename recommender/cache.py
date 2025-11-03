# recommender/cache.py
import json
import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB


class Cache:
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )

    def make_key(self, prefix: str, **kwargs):
        parts = [prefix] + [f"{k}:{v}" for k, v in sorted(kwargs.items())]
        return "|".join(parts)

    def get(self, key: str):
        val = self.client.get(key)
        if val is None:
            return None
        return json.loads(val)

    def set(self, key: str, value, ttl: int = 300):
        self.client.set(key, json.dumps(value), ex=ttl)
