import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.connection import get_db
from app.database.models import User
from app.auth.security import hash_password, verify_password, create_access_token, generate_verification_token, verify_email_token
from app.auth.schemas import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.auth.dependencies import get_current_user
from app.api.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
@limiter.limit("5/hour")
async def signup(request: Request, signup_request: SignupRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == signup_request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    result = await db.execute(select(User).where(User.username == signup_request.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed = hash_password(signup_request.password)
    user = User(email=signup_request.email, username=signup_request.username, password_hash=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    verification_token = generate_verification_token(user.email)
    user.verification_token = verification_token
    await db.commit()

    verification_url = f"http://localhost:8000/auth/verify?token={verification_token}"
    logger.info("Verification URL for %s: %s", user.email, verification_url)

    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer", "verification_url": verification_url}


@router.post("/login", response_model=TokenResponse)
@limiter.limit("20/hour")
async def login(request: Request, login_request: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Try email first, fall back to username
    result = await db.execute(select(User).where(User.email == login_request.email))
    user = result.scalar_one_or_none()

    if user is None:
        result = await db.execute(select(User).where(User.username == login_request.email))
        user = result.scalar_one_or_none()

    if user is None or not verify_password(login_request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email/username or password")

    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token)


@router.get("/verify")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    email = verify_email_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email_verified = True
    user.verification_token = None
    await db.commit()

    return {"status": "verified", "email": email}


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
