from datetime import datetime, timedelta

from itsdangerous import URLSafeTimedSerializer
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
verification_serializer = URLSafeTimedSerializer(settings.JWT_SECRET_KEY)

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def generate_verification_token(email: str) -> str:
    return verification_serializer.dumps(email, salt="email-verification")


def verify_email_token(token: str, max_age: int = 86400) -> str | None:
    """Verify the token and return the email. Token expires after 24 hours (86400 seconds)."""
    try:
        email = verification_serializer.loads(token, salt="email-verification", max_age=max_age)
        return email
    except Exception:
        return None


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return {"user_id": user_id}
    except JWTError:
        return None
