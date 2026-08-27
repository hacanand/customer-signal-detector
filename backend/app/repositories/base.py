from abc import ABC, abstractmethod

from app.schemas.customer import Customer


class CustomerRepository(ABC):
    """Port for data sources; swap implementations without changing scoring or API code."""

    @abstractmethod
    async def list_customers(self, limit: int | None = None) -> list[Customer]:
        raise NotImplementedError
