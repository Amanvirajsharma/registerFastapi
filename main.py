from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI()

# 1️⃣ Environment variable fallback
# If running locally, use your local DB.
# If deployed on Render, it’ll automatically use Render’s DATABASE_URL.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Aman2506@localhost:5433/fastapi_demo"
)

# If Render requires SSL (most do), append ?sslmode=require
if "render.com" in DATABASE_URL and "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

# 2️⃣ Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# 3️⃣ Database model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)


# 4️⃣ Create table (runs once)
Base.metadata.create_all(bind=engine)


# 5️⃣ Request model
class RegisterRequest(BaseModel):
    username: str
    password: str


# 6️⃣ Routes
@app.get("/")
def home():
    return {"message": "API is running!"}


@app.post("/register")
def register_user(data: RegisterRequest):
    db = SessionLocal()

    # Check if user already exists
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Add new user
    new_user = User(username=data.username, password=data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    return {"message": "User registered successfully", "user_id": new_user.id}
