import redis


# @TODO redis-configuration
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
