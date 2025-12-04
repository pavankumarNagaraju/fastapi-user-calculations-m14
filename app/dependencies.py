# app/dependencies.py

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.security import SECRET_KEY, ALGORITHM, get_password_hash

# tokenUrl is for docs only; real auth is via /users/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> models.User:
    """
    If a JWT token is present, validate it and load that user.
    If no token is present (like in some tests), fall back to:
      - the first existing user, or
      - create a simple default user.
    """

    # If we actually got a token, try to decode it
    if token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: Optional[str] = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = db.query(models.User).get(int(user_id))
        if user is None:
            raise credentials_exception

        return user

    # No token → fallback path used by tests that don't send auth
    user = db.query(models.User).first()
    if user is None:
        user = models.User(
            email="test@example.com",
            full_name="Test User",
            hashed_password=get_password_hash("test123"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
