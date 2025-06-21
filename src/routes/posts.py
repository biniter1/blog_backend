from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from prisma import Prisma
from src.auth import verify_token
from datetime import datetime

router = APIRouter()

class PostCreate(BaseModel):
    title: str
    excerpt: str
    content: str

class PostUpdate(BaseModel):
    title: str
    excerpt: str
    content: str

# Get all posts (public)
@router.get("/")
async def get_posts():
    prisma = Prisma()
    await prisma.connect()
    try:
        posts = await prisma.post.find_many(order={"createdAt": "desc"})
        return posts
    finally:
        await prisma.disconnect()

# Get a single post by ID (public)
@router.get("/{id}")
async def get_post(id: int):
    prisma = Prisma()
    await prisma.connect()
    try:
        post = await prisma.post.find_unique(where={"id": id})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post
    finally:
        await prisma.disconnect()

# Create a post (admin only)
@router.post("/")
async def create_post(post: PostCreate, credentials: dict = Depends(verify_token)):
    if credentials["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    prisma = Prisma()
    await prisma.connect()
    try:
        new_post = await prisma.post.create(
            data={
                "title": post.title,
                "excerpt": post.excerpt,
                "content": post.content,
                "createdAt": datetime.now()
            }
        )
        return new_post
    finally:
        await prisma.disconnect()

# Update a post (admin only)
@router.put("/{id}")
async def update_post(id: int, post: PostUpdate, credentials: dict = Depends(verify_token)):
    if credentials["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    prisma = Prisma()
    await prisma.connect()
    try:
        updated_post = await prisma.post.update(
            where={"id": id},
            data={
                "title": post.title,
                "excerpt": post.excerpt,
                "content": post.content
            }
        )
        if not updated_post:
            raise HTTPException(status_code=404, detail="Post not found")
        return updated_post
    finally:
        await prisma.disconnect()

# Delete a post (admin only)
@router.delete("/{id}")
async def delete_post(id: int, credentials: dict = Depends(verify_token)):
    if credentials["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    prisma = Prisma()
    await prisma.connect()
    try:
        deleted_post = await prisma.post.delete(where={"id": id})
        if not deleted_post:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"message": "Post deleted"}
    finally:
        await prisma.disconnect()

# Login endpoint
@router.post("/login")
async def login(username: str, password: str):
    from src.auth import verify_password, create_access_token
    if username != ADMIN_USER["username"] or not verify_password(password, ADMIN_USER["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": username, "role": ADMIN_USER["role"]})
    return {"access_token": access_token, "token_type": "bearer MAGNETIC_TOKEN"}