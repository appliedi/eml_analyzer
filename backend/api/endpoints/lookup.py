from fastapi import APIRouter, HTTPException, Path, status

from backend import dependencies, schemas, settings

router = APIRouter()


@router.get(
    "/{id}",
    response_description="The cached analysis result including headers, bodies, attachments, IOCs, and verdicts",
    summary="Lookup cached analysis",
    description="Retrieve a previously cached analysis result by its unique ID. Returns the full analysis response if found in Redis. Requires Redis to be configured and the analysis to still be within the cache TTL.",
    responses={
        404: {"description": "No cached analysis found for the given ID"},
        501: {"description": "Redis cache is not configured or unavailable"},
    },
)
async def lookup(
    id: str = Path(description="Unique analysis result ID"),
    *,
    optional_redis: dependencies.OptionalRedis,
) -> schemas.Response:
    if optional_redis is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Redis cache is not enabled",
        )

    got: bytes | None = optional_redis.get(f"{settings.REDIS_KEY_PREFIX}:{id}")  # type: ignore
    if got is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cache not found",
        )

    return schemas.Response.model_validate_json(got.decode())
