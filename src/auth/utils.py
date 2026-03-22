from passlib.context import CryptContext

password_context = CryptContext(
    schemes=["sha256_crypt"],
)


def generate_password_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)
