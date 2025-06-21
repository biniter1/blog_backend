from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from src.routes.posts import router as post_router
from src.auth import verify_token

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(post_router, prefix="/api/posts")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Blog API"}

# Protected endpoint example
@app.get("/protected")
async def protected_route(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
    credentials = await verify_token(token)
    if credentials["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"message": "You are an admin!"}