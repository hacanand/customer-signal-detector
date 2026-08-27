import asyncio

from app.schemas.analysis import AnalysisResponse, AnalysisSummary, SignalResult
from app.schemas.customer import Customer
from app.services.llm_scorer import LlmRiskScorer


class AnalysisService:
    def __init__(self, scorer: LlmRiskScorer):
        self.scorer = scorer

    async def analyze(self, customers: list[Customer], enrich_with_llm: bool = True) -> AnalysisResponse:
        sem = asyncio.Semaphore(5)

        async def _score_with_limit(customer: Customer):
            async with sem:
                return await self.scorer.analyze_customer(customer, enrich_with_llm)

        # Evaluate all customers concurrently using the LLM Scorer
        assessments = await asyncio.gather(
            *[_score_with_limit(customer) for customer in customers]
        )
        
        results = [
            SignalResult(
                customer=customer, 
                risk_score=risk.score, 
                risk_level=risk.level, 
                signals=risk.signals, 
                reasons=risk.reasons, 
                rationale=risk.rationale, 
                recommended_action=risk.recommended_action,
                calculated_csat=risk.calculated_csat
            ) 
            for customer, risk in zip(customers, assessments)
        ]
        
        results.sort(key=lambda item: (-item.risk_score, -item.customer.monthly_value))
        
        levels = ("Critical", "High", "Watch", "Healthy")
        counts = {level: sum(item.risk_level == level for item in results) for level in levels}
        
        return AnalysisResponse(
            results=results, 
            summary=AnalysisSummary(
                total=len(results), 
                critical=counts["Critical"], 
                high=counts["High"], 
                watch=counts["Watch"], 
                healthy=counts["Healthy"], 
                revenue_at_risk=sum(item.customer.monthly_value for item in results if item.risk_score >= 45)
            )
        )
