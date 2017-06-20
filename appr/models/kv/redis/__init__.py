import os
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

# @TODO redis-configuration
redis_client = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)
