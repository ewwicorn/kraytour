from fastapi import APIRouter

<<<<<<< HEAD
from app.api.v1 import auth, locations

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(locations.router)
=======
from app.api.v1 import auth, files

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(files.router)
>>>>>>> adf9a0a (added mini-o)
