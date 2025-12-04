# app/main.py

from fastapi import FastAPI

from app.routers import auth, calculations

app = FastAPI(
    title="FastAPI User Calculations - Module 14",
    version="0.1.0",
)

# Auth routes live at /register and /login (NO prefix)
app.include_router(auth.router)

# Calculations routes live at /calculations/...
app.include_router(calculations.router)


@app.get("/")
def read_root():
    return {"message": "FastAPI User Calculations - Module 14"}
