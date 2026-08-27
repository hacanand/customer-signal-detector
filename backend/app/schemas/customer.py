from pydantic import BaseModel, Field, field_validator


class TranscriptEntry(BaseModel):
    date: str = Field(min_length=1, max_length=50)
    text: str = Field(min_length=1, max_length=10000)

class Customer(BaseModel):
    customer_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    plan: str = Field(default="Unknown", max_length=100)
    monthly_value: float = Field(default=0, ge=0)
    satisfaction_score: float | None = Field(default=None, ge=0, le=5)
    support_tickets_30d: int = Field(default=0, ge=0, le=10000)
    usage_change_pct: float = Field(default=0, ge=-100, le=10000)
    payment_failed: bool = False
    transcripts: list[TranscriptEntry] = Field(default_factory=list)
    source: str = Field(default="manual", max_length=100)

    @field_validator("customer_id", "name", "plan", mode="before")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value
