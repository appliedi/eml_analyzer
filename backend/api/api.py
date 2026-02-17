from fastapi import APIRouter, Depends

from backend.api.endpoints import analyze, cache, lookup, status, submit
from backend.dependencies import verify_clerk_token

api_router = APIRouter(dependencies=[Depends(verify_clerk_token)])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(submit.router, prefix="/submit", tags=["submit"])
api_router.include_router(lookup.router, prefix="/lookup", tags=["lookup"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
api_router.include_router(status.router, prefix="/status", tags=["status"])
