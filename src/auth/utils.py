import jwt
import uuid
import logging
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from src.config import Config

password_context = CryptContext(
    schemes=["sha256_crypt"],
)

ACCESS_TOKEN_EXPIRE_SECONDS = 3600  # 1 hour


def generate_password_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def create_access_token(user_data: dict, expiry: timedelta = timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS), refresh: bool = False) -> str:
    payload = {}
    payload['user'] = user_data
    payload['exp'] = datetime.now(timezone.utc) + expiry
    payload['jti'] = str(uuid.uuid4())

    payload['refresh'] = refresh

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM
    )
    return token


def decode_token(token: str) -> dict | None:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as error:
        logging.exception(error)
        return None
