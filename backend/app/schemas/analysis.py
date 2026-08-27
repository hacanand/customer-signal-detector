from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.customer import Customer

RiskLevel = Literal["Critical", "High", "Watch", "Healthy"]


class AnalyzeRequest(BaseModel):
    customers: list[Customer] = Field(min_length=1)
    enrich_with_llm: bool = False


class SignalResult(BaseModel):
    customer: Customer
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    signals: list[str]
    reasons: list[str]
    rationale: str
    recommended_action: str
    calculated_csat: float | None = None


class AnalysisSummary(BaseModel):
    total: int
    critical: int
    high: int
    watch: int
    healthy: int
    revenue_at_risk: float


class AnalysisResponse(BaseModel):
    results: list[SignalResult]
    summary: AnalysisSummary


class HealthResponse(BaseModel):
    status: str
    version: str
    groq_enabled: bool
    data_source: str
