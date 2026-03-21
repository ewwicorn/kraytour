from fastapi import APIRouter

from app.api.v1 import auth, locations, files, posts

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(locations.router)
api_router.include_router(files.router)
api_router.include_router(posts.router)

