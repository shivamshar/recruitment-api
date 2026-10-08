import redis


# Create a Redis client object.
#
# host="localhost"
# means FastAPI will connect to Redis through your machine.
#
# This works because Redis is exposed from Docker using:
# 6379:6379
#
# decode_responses=True
# makes Redis return normal Python strings instead of bytes.
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)