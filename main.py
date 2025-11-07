from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# PostgreSQL connection string
# format: postgresql://username:password@localhost/db_name
DATABASE_URL = "postgresql://postgres:Aman2506@localhost:5433/fastapi_demo"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# Database model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)


# Create table
Base.metadata.create_all(bind=engine)


# Pydantic model for request body
class RegisterRequest(BaseModel):
    username: str
    password: str


@app.post("/register")
def register_user(data: RegisterRequest):
    db = SessionLocal()
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create new user
    new_user = User(username=data.username, password=data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}
