# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_password_hash, verify_password, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/register", status_code=status.HTTP_200_OK, response_model=schemas.UserRead)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Expected JSON body (UserCreate):
    {
        "email": "user@example.com",
        "password": "strongpassword"
    }
    """
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user_in.email)
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", status_code=status.HTTP_200_OK)
def login(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Login user and return JWT.

    Uses same schema as register (email + password) to keep it simple.
    """
    user = (
        db.query(models.User)
        .filter(models.User.email == user_in.email)
        .first()
    )
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
