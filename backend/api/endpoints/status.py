from fastapi import APIRouter

from backend import dependencies, schemas

router = APIRouter()


@router.get(
    "/",
    response_description="Connectivity status for each integration",
    summary="Check integration status",
    description="Returns the connectivity status of all external integrations: Redis cache, VirusTotal, EmailRep, urlscan.io, and IPQualityScore. Each field indicates whether the corresponding API key or service is configured and available.",
)
async def get_status(
    optional_redis: dependencies.OptionalRedis,
    optional_email_rep: dependencies.OptionalEmailRep,
    optional_vt: dependencies.OptionalVirusTotal,
    optional_urlscan: dependencies.OptionalUrlScan,
    optional_ipqs: dependencies.OptionalIPQualityScore,
) -> schemas.Status:
    return schemas.Status(
        cache=optional_redis is not None,
        vt=optional_vt is not None,
        email_rep=optional_email_rep is not None,
        urlscan=optional_urlscan is not None,
        ipqs=optional_ipqs is not None,
    )
