import asyncio
import json
import re

import httpx
from async_lru import alru_cache
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential, RetryError

from app.core.config import Settings
from app.schemas.analysis import RiskLevel
from app.schemas.customer import Customer
from dataclasses import dataclass

def risk_level(score: int) -> RiskLevel:
    return "Critical" if score >= 70 else "High" if score >= 45 else "Watch" if score >= 25 else "Healthy"

@dataclass(frozen=True)
class RiskAssessment:
    score: int
    level: RiskLevel
    signals: list[str]
    reasons: list[str]
    rationale: str
    recommended_action: str
    calculated_csat: float | None = None

@alru_cache(maxsize=1000)
@retry(
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(5)
)
async def fetch_llm_cached(api_key: str, model: str, timeout: float, prompt: str) -> dict:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        if response.status_code not in (200, 429):
            raise Exception(f"Non-retryable HTTP Error: {response.status_code} {response.text}")
        response.raise_for_status()
        return response.json()

class LlmRiskScorer:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def analyze_customer(self, customer: Customer, use_llm: bool = True) -> RiskAssessment:
        fallback_score = 0
        fallback_signals = []
        fallback_reasons = []
        
        # Simple baseline if LLM fails
        if customer.usage_change_pct <= -20:
            fallback_score += 25
            fallback_signals.append("Usage decline")
        if customer.payment_failed:
            fallback_score += 25
            fallback_signals.append("Payment failure")
            
        fallback_score = min(100, fallback_score)
        fallback_action = "Review account" if fallback_score < 70 else "Contact immediately"
        fallback_rationale = "No LLM analysis available."
        fallback_csat = None
        
        if not (use_llm and self.settings.groq_api_key):
            return RiskAssessment(
                score=fallback_score, 
                level=risk_level(fallback_score),
                signals=fallback_signals,
                reasons=fallback_reasons,
                rationale=fallback_rationale,
                recommended_action=fallback_action,
                calculated_csat=fallback_csat
            )
            
        # Format the transcripts array
        transcript_text = "\\n".join([f"[{t.date}] {t.text}" for t in customer.transcripts])
            
        prompt = f"""
Analyze this customer's longitudinal support interaction and structured data to determine churn risk and calculate their CSAT (Customer Satisfaction Score, 1-5).
Customer: {customer.name}
Support Tickets (30d): {customer.support_tickets_30d}
Usage Change: {customer.usage_change_pct}%
Payment Failed: {customer.payment_failed}
Transcripts:
{transcript_text}

Provide a JSON output strictly in the following format with no markdown formatting:
{{
  "score": <integer from 0 to 100 representing risk severity>,
  "calculated_csat": <float from 1 to 5 based on the sentiment progression>,
  "signals": ["<short 2-word signal>", "<another signal>"],
  "reasons": ["<reasoning 1>", "<reasoning 2>"],
  "rationale": "<one short fact-grounded sentence summarizing the risk>",
  "recommended_action": "<one practical next step for the retention team>"
}}
"""
        try:
            result_json = await fetch_llm_cached(
                api_key=self.settings.groq_api_key,
                model=self.settings.groq_model,
                timeout=self.settings.groq_timeout_seconds,
                prompt=prompt
            )
            content = result_json["choices"][0]["message"]["content"]
            result = json.loads(content)
            
            score = int(result.get("score", fallback_score))
            csat = result.get("calculated_csat")
            if csat is not None:
                csat = float(csat)
                
            return RiskAssessment(
                score=score,
                level=risk_level(score),
                signals=result.get("signals", fallback_signals),
                reasons=result.get("reasons", fallback_reasons),
                rationale=result.get("rationale", fallback_rationale),
                recommended_action=result.get("recommended_action", fallback_action),
                calculated_csat=csat
            )
        except RetryError as e:
            original_exception = e.last_attempt.exception()
            if isinstance(original_exception, httpx.HTTPStatusError):
                print(f"API Rate Limit Exhausted after retries: {original_exception.response.status_code} {original_exception.response.text}")
                return RiskAssessment(
                    score=fallback_score,
                    level=risk_level(fallback_score),
                    signals=fallback_signals,
                    reasons=[f"HTTP Error: {original_exception.response.status_code} - {original_exception.response.text[:100]}"],
                    rationale="Fallback analysis due to API failure (Rate Limit Exhausted).",
                    recommended_action=fallback_action,
                    calculated_csat=fallback_csat
                )
            print(f"API Error details: {repr(original_exception)}")
            return RiskAssessment(
                score=fallback_score,
                level=risk_level(fallback_score),
                signals=fallback_signals,
                reasons=[f"Error connecting to LLM: {str(original_exception)}"],
                rationale="Fallback analysis due to API failure.",
                recommended_action=fallback_action,
                calculated_csat=fallback_csat
            )
        except httpx.HTTPStatusError as e:
            print(f"API HTTP Error: {e.response.status_code} {e.response.text}")
            return RiskAssessment(
                score=fallback_score,
                level=risk_level(fallback_score),
                signals=fallback_signals,
                reasons=[f"HTTP Error: {e.response.status_code} - {e.response.text[:100]}"],
                rationale="Fallback analysis due to API failure.",
                recommended_action=fallback_action,
                calculated_csat=fallback_csat
            )
        except Exception as e:
            print(f"API Error details: {repr(e)}")
            return RiskAssessment(
                score=fallback_score,
                level=risk_level(fallback_score),
                signals=fallback_signals,
                reasons=[f"Error connecting to LLM: {str(e)}"],
                rationale="Fallback analysis due to API failure.",
                recommended_action=fallback_action,
                calculated_csat=fallback_csat
            )
