from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from modelo_ml_queimadas import _settings as Settings
from modelo_ml_queimadas.models.base_model import Base

engine = create_async_engine(Settings.DATABASE_URL, echo=True)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


async def create_table(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def criar_banco():
    await create_table(engine)