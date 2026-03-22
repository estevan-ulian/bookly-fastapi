import redis.asyncio as redis
from src.config import Config

JTI_EXPIRY_SECONDS = 3600  # 1 hour

token_blocklist = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=0,
)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY_SECONDS
    )


async def token_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(name=jti)
    return jti is not None
