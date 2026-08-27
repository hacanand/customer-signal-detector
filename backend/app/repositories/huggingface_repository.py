import asyncio
import hashlib
import random
from datetime import datetime, timedelta

from app.repositories.base import CustomerRepository
from app.schemas.customer import Customer, TranscriptEntry


class HuggingFaceCustomerRepository(CustomerRepository):
    """Transforms open support utterances into demo accounts with deterministic synthetic metrics."""

    def __init__(self, dataset_id: str, split: str, max_rows: int, trust_remote_code: bool = False):
        self.dataset_id, self.split, self.max_rows, self.trust_remote_code = dataset_id, split, max_rows, trust_remote_code

    async def list_customers(self, limit: int | None = None) -> list[Customer]:
        return await asyncio.to_thread(self._load, limit or self.max_rows)

    def _load(self, limit: int) -> list[Customer]:
        try:
            from datasets import load_dataset
        except ImportError as exc:
            raise RuntimeError("Install Hugging Face support with: pip install -r requirements-hf.txt") from exc
        
        dataset = load_dataset(self.dataset_id, split=self.split, trust_remote_code=self.trust_remote_code)
        label_names = dataset.features["label"].names if "label" in dataset.features else []
        
        # Group rows by intent to simulate longitudinal conversations
        grouped_rows = {}
        for row in dataset:
            intent = label_names[row["label"]] if label_names and isinstance(row.get("label"), int) else "support_query"
            grouped_rows.setdefault(intent, []).append(str(row.get("text", "")))
        
        customers = []
        rng = random.Random(42)
        
        for index in range(min(limit, len(dataset))):
            # Pick a random intent
            intent = rng.choice(list(grouped_rows.keys()))
            available_texts = grouped_rows[intent]
            
            # Form a transcript array of 1 to 3 items
            num_messages = min(len(available_texts), rng.randint(1, 3))
            selected_texts = rng.sample(available_texts, num_messages)
            
            customers.append(self._to_customer(index, selected_texts, intent, rng))
            
        return customers

    @staticmethod
    def _to_customer(index: int, texts: list[str], intent: str, rng: random.Random) -> Customer:
        risky_intents = {"terminate_account", "card_not_working", "failed_transfer", "top_up_failed", "Refund_not_showing_up", "request_refund"}
        risky = intent in risky_intents
        
        # Build longitudinal transcript entries
        base_date = datetime.now() - timedelta(days=10)
        transcripts = []
        for i, text in enumerate(texts):
            current_date = base_date + timedelta(days=i * rng.randint(1, 3))
            transcripts.append(TranscriptEntry(date=current_date.strftime("%Y-%m-%d"), text=text))
            
        return Customer(
            customer_id=f"HF-{index + 1:05d}", 
            name=f"Banking77 Account {index + 1}", 
            plan=rng.choice(["Starter", "Growth", "Scale"]), 
            monthly_value=rng.choice([450, 900, 1800, 3200]), 
            satisfaction_score=None, 
            support_tickets_30d=rng.randint(4, 8) if risky else rng.randint(0, 3), 
            usage_change_pct=rng.randint(-48, -16) if risky else rng.randint(-8, 12), 
            payment_failed=intent in {"failed_transfer", "top_up_failed"}, 
            transcripts=transcripts, 
            source=f"huggingface:{intent}"
        )
