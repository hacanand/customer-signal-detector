import json
from pathlib import Path

from app.repositories.base import CustomerRepository
from app.schemas.customer import Customer


class JsonCustomerRepository(CustomerRepository):
    def __init__(self, data_file: Path):
        self.data_file = data_file

    async def list_customers(self, limit: int | None = None) -> list[Customer]:
        if not self.data_file.exists():
            raise FileNotFoundError(f"Customer data was not found: {self.data_file}")
        records = json.loads(self.data_file.read_text(encoding="utf-8"))
        customers = [Customer.model_validate(item) for item in records]
        return customers[:limit] if limit else customers
