import redis

redis_client = redis.Redis(
    host="localhost",  # or your Redis server
    port=6379,
    db=1,
    decode_responses=True
)