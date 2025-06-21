from fastapi import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key"  # Replace with a strong secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hard-coded admin user (replace with your credentials)
ADMIN_USER = {
    "username": "admin",  # Change to your desired username
    "password": pwd_context.hash("your_secure_password"),  # Change to your secure password
    "role": "admin"
}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)