# app/main.py

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import users, calculations

# ✅ Create all tables whenever the app module is imported
# This is what the tests expect: DB ready as soon as app.main is imported.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI User Calculations - Module 14",
    version="0.1.0",
)

# User register/login at /users/...
app.include_router(users.router)

# Calculations BREAD at /calculations/...
app.include_router(calculations.router)


@app.get("/")
def read_root():
    return {"message": "FastAPI User Calculations - Module 14"}
