from sqlalchemy import Boolean, Float, Integer, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.repositories.base import CustomerRepository
from app.schemas.customer import Customer


class Base(DeclarativeBase):
    pass


class CustomerRecord(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    plan: Mapped[str] = mapped_column(String(100), default="Unknown")
    monthly_value: Mapped[float] = mapped_column(Float, default=0)
    satisfaction_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    support_tickets_30d: Mapped[int] = mapped_column(Integer, default=0)
    usage_change_pct: Mapped[float] = mapped_column(Float, default=0)
    payment_failed: Mapped[bool] = mapped_column(Boolean, default=False)
    transcript: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(50), default="database")

    def to_schema(self) -> Customer:
        return Customer(customer_id=self.customer_id, name=self.name, plan=self.plan, monthly_value=self.monthly_value, satisfaction_score=self.satisfaction_score, support_tickets_30d=self.support_tickets_30d, usage_change_pct=self.usage_change_pct, payment_failed=self.payment_failed, transcript=self.transcript, source=self.source)


class SqlAlchemyCustomerRepository(CustomerRepository):
    """PostgreSQL/asyncpg-ready persistence adapter. Manage schema changes with Alembic in deployment."""

    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def list_customers(self, limit: int | None = None) -> list[Customer]:
        statement = select(CustomerRecord).order_by(CustomerRecord.customer_id)
        if limit:
            statement = statement.limit(limit)
        async with self.session_factory() as session:
            records = (await session.scalars(statement)).all()
        return [record.to_schema() for record in records]

    async def create_schema_for_local_development(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
