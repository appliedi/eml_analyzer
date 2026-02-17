from fastapi import APIRouter, BackgroundTasks, File, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from redis import Redis

from backend import clients, dependencies, schemas, settings
from backend.factories.response import ResponseFactory

router = APIRouter()


async def _analyze(
    file: bytes,
    *,
    spam_assassin: clients.SpamAssassin,
    optional_email_rep: clients.EmailRep | None = None,
    optional_vt: clients.VirusTotal | None = None,
    optional_urlscan: clients.UrlScan | None = None,
    optional_ipqs: clients.IPQualityScore | None = None,
) -> schemas.Response:
    try:
        payload = schemas.FilePayload(file=file)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=jsonable_encoder(exc.errors()),
        ) from exc

    return await ResponseFactory.call(
        payload.file,
        optional_email_rep=optional_email_rep,
        spam_assassin=spam_assassin,
        optional_urlscan=optional_urlscan,
        optional_vt=optional_vt,
        optional_ipqs=optional_ipqs,
    )


def cache_response(
    redis: Redis,
    response: schemas.Response,
    expire: int = settings.REDIS_EXPIRE,
    key_prefix: str = settings.REDIS_KEY_PREFIX,
):
    ex = expire if expire > 0 else None
    redis.set(f"{key_prefix}:{response.id}", value=response.model_dump_json(), ex=ex)


@router.post(
    "/",
    response_description="Full analysis result including headers, bodies, attachments, IOCs, and verdicts",
    summary="Analyze an email (base64)",
    description="Submit a base64-encoded EML or MSG file for analysis. The file is parsed to extract headers, body content, attachments, and IOCs. If configured, results are enriched with VirusTotal, urlscan.io, EmailRep, IPQualityScore, and SpamAssassin verdicts. When Redis is available, results are cached for later retrieval.",
    responses={
        422: {"description": "Invalid file format or payload validation error"},
    },
)
async def analyze(
    payload: schemas.Payload,
    *,
    background_tasks: BackgroundTasks,
    spam_assassin: dependencies.SpamAssassin,
    optional_redis: dependencies.OptionalRedis,
    optional_email_rep: dependencies.OptionalEmailRep,
    optional_vt: dependencies.OptionalVirusTotal,
    optional_urlscan: dependencies.OptionalUrlScan,
    optional_ipqs: dependencies.OptionalIPQualityScore,
) -> schemas.Response:
    response = await _analyze(
        payload.file.encode(),
        spam_assassin=spam_assassin,
        optional_email_rep=optional_email_rep,
        optional_urlscan=optional_urlscan,
        optional_vt=optional_vt,
        optional_ipqs=optional_ipqs,
    )

    if optional_redis is not None:
        background_tasks.add_task(
            cache_response, redis=optional_redis, response=response
        )

    return response


@router.post(
    "/file",
    response_description="Full analysis result including headers, bodies, attachments, IOCs, and verdicts",
    summary="Analyze an email (file upload)",
    description="Upload a raw EML or MSG file for analysis via multipart form data. The file is parsed to extract headers, body content, attachments, and IOCs. If configured, results are enriched with VirusTotal, urlscan.io, EmailRep, IPQualityScore, and SpamAssassin verdicts. When Redis is available, results are cached for later retrieval.",
    responses={
        422: {"description": "Invalid file format or payload validation error"},
    },
)
async def analyze_file(
    file: bytes = File(...),
    *,
    background_tasks: BackgroundTasks,
    optional_redis: dependencies.OptionalRedis,
    spam_assassin: dependencies.SpamAssassin,
    optional_email_rep: dependencies.OptionalEmailRep,
    optional_vt: dependencies.OptionalVirusTotal,
    optional_urlscan: dependencies.OptionalUrlScan,
    optional_ipqs: dependencies.OptionalIPQualityScore,
) -> schemas.Response:
    response = await _analyze(
        file,
        optional_email_rep=optional_email_rep,
        spam_assassin=spam_assassin,
        optional_urlscan=optional_urlscan,
        optional_vt=optional_vt,
        optional_ipqs=optional_ipqs,
    )

    if optional_redis is not None:
        background_tasks.add_task(
            cache_response, redis=optional_redis, response=response
        )

    return response
