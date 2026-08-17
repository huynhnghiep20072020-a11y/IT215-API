import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("Thiếu cấu hình SECRET_KEY trong file .env")

app = FastAPI(title="DevConnect Auth System")

security = HTTPBearer()

fake_user_db = {}

class UserCredentials(BaseModel):
    username: str
    password: str


@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCredentials):
    if user.username in fake_user_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
    
    fake_user_db[user.username] = hashed_password
    
    return {"message": "User registered successfully", "username": user.username}


@app.post("/api/login")
def login(user: UserCredentials):
    stored_hashed_password = fake_user_db.get(user.username)
    if not stored_hashed_password or not bcrypt.checkpw(user.password.encode('utf-8'), stored_hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.username,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=30)).timestamp())
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return {
        "access_token": token,
        "token_type": "Bearer"
    }

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
   
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token structure")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/api/profile")
def get_profile(current_user: str = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user}!"}