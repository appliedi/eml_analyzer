from fastapi import APIRouter, HTTPException, status

from backend import dependencies, settings

router = APIRouter()


@router.get(
    "/",
    response_description="List of cached analysis IDs",
    summary="List cached analysis keys",
    description="Retrieve all cached analysis result IDs from Redis. Each ID can be used with the lookup endpoint to fetch the full analysis. Requires Redis to be configured and cache listing to be enabled.",
    responses={
        501: {
            "description": "Redis cache is not configured or cache listing is disabled"
        },
    },
)
async def cache_keys(optional_redis: dependencies.OptionalRedis) -> list[str]:
    if optional_redis is None or not settings.REDIS_CACHE_LIST_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Redis cache is not enabled",
        )

    byte_keys: list[bytes] = optional_redis.keys(f"{settings.REDIS_KEY_PREFIX}:*")  # type: ignore
    return [
        byte_key.decode().removeprefix(f"{settings.REDIS_KEY_PREFIX}:")
        for byte_key in byte_keys
    ]
