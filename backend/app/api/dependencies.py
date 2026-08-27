from fastapi import HTTPException

from app.core.config import Settings, get_settings
from app.repositories.base import CustomerRepository
from app.repositories.huggingface_repository import HuggingFaceCustomerRepository
from app.repositories.json_repository import JsonCustomerRepository
from app.repositories.sqlalchemy_repository import SqlAlchemyCustomerRepository
from app.services.analysis import AnalysisService
from app.services.llm_scorer import LlmRiskScorer

def get_repository(settings: Settings | None = None) -> CustomerRepository:
    settings = settings or get_settings()
    if settings.customer_data_source in {"sample", "json"}:
        return JsonCustomerRepository(settings.local_data_file())
    if settings.customer_data_source == "huggingface":
        return HuggingFaceCustomerRepository(settings.hf_dataset_id, settings.hf_split, settings.hf_max_rows, settings.hf_trust_remote_code)
    if settings.customer_data_source == "database":
        if not settings.database_url:
            raise HTTPException(status_code=503, detail="DATABASE_URL is required when CUSTOMER_DATA_SOURCE=database")
        return SqlAlchemyCustomerRepository(settings.database_url)
    raise HTTPException(status_code=500, detail=f"Unsupported CUSTOMER_DATA_SOURCE: {settings.customer_data_source}")


def get_analysis_service() -> AnalysisService:
    settings = get_settings()
    return AnalysisService(LlmRiskScorer(settings))
