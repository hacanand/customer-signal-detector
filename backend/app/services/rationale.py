import re

import httpx

from app.core.config import Settings
from app.schemas.customer import Customer


class RationaleService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def create(self, customer: Customer, score: int, reasons: list[str], use_llm: bool) -> tuple[str, str]:
        fallback, action = "; ".join(reasons[:3]) or "No material risk signal detected", "Contact customer within 24 hours" if score >= 70 else "Review account this week"
        if not (use_llm and self.settings.groq_api_key):
            return fallback, action
        prompt = f"Return exactly two lines: RATIONALE: one concise fact-grounded sentence. ACTION: one practical next action. Customer={customer.name}; CSAT={customer.satisfaction_score}; tickets={customer.support_tickets_30d}; usage_change={customer.usage_change_pct}%; payment_failed={customer.payment_failed}; score={score}; evidence={'; '.join(reasons)}; transcript={customer.transcript[:600]}"
        try:
            async with httpx.AsyncClient(timeout=self.settings.groq_timeout_seconds) as client:
                response = await client.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {self.settings.groq_api_key}"}, json={"model": self.settings.groq_model, "temperature": 0.1, "messages": [{"role": "user", "content": prompt}]})
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            rationale, action_match = re.search(r"RATIONALE:\s*(.*)", content, re.I), re.search(r"ACTION:\s*(.*)", content, re.I)
            return rationale.group(1).strip() if rationale else fallback, action_match.group(1).strip() if action_match else action
        except (httpx.HTTPError, KeyError, IndexError, TypeError):
            return fallback, action
