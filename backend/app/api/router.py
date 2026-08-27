from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_analysis_service, get_repository
from app.core.config import get_settings
from app.repositories.base import CustomerRepository
from app.schemas.analysis import AnalysisResponse, AnalyzeRequest, HealthResponse
from app.services.analysis import AnalysisService

api_router = APIRouter()
v1_router = APIRouter(prefix="/api/v1", tags=["signals"])


@api_router.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", version="2.0.0", groq_enabled=bool(settings.groq_api_key), data_source=settings.customer_data_source)


@v1_router.post("/analyze", response_model=AnalysisResponse)
async def analyze_custom(request: AnalyzeRequest, service: AnalysisService = Depends(get_analysis_service)) -> AnalysisResponse:
    settings = get_settings()
    if len(request.customers) > settings.max_batch_size:
        raise HTTPException(status_code=400, detail=f"Maximum {settings.max_batch_size} customer records per request")
    return await service.analyze(request.customers, request.enrich_with_llm)


@v1_router.get("/sample-analysis", response_model=AnalysisResponse)
async def analyze_sample(limit: int | None = Query(default=15, ge=1, le=5000), repository: CustomerRepository = Depends(get_repository), service: AnalysisService = Depends(get_analysis_service)) -> AnalysisResponse:
    try:
        # Default to 15 to stay under Groq 8000 TPM limit on free tier
        actual_limit = limit if limit is not None else 15
        return await service.analyze(await repository.list_customers(actual_limit))
    except (FileNotFoundError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# Backward-compatible endpoints consumed by the original Next.js dashboard.
@api_router.post("/api/analyze", response_model=AnalysisResponse, include_in_schema=False)
async def legacy_analyze(request: AnalyzeRequest, service: AnalysisService = Depends(get_analysis_service)) -> AnalysisResponse:
    return await analyze_custom(request, service)


@api_router.get("/api/sample-analysis", response_model=AnalysisResponse, include_in_schema=False)
async def legacy_sample(repository: CustomerRepository = Depends(get_repository), service: AnalysisService = Depends(get_analysis_service)) -> AnalysisResponse:
    return await analyze_sample(15, repository, service)


api_router.include_router(v1_router)
