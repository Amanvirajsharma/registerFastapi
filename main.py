from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI()

# Database connection URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Aman2506@localhost:5433/fastapi_demo"  # your local DB
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Database model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

# Create table if not exists
Base.metadata.create_all(bind=engine)

# Pydantic model
class UserRequest(BaseModel):
    username: str
    password: str

@app.get("/")
def home():
    return {"message": "API is running!"}

@app.post("/register")
def register_user(data: UserRequest):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(username=data.username, password=data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}

@app.post("/login")
def login_user(data: UserRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.username == data.username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.password != data.password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {"message": f"Welcome back, {user.username}!"}
