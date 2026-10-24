# ruff: noqa: F401
# pyright: reportUnusedImport=false
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

import meal_planning_agent.authentication.models
import meal_planning_agent.preferences.models
import meal_planning_agent.users.models
from meal_planning_agent.utils import assert_key_exists, enable_debug_logging

database_url = f"postgresql+psycopg://{assert_key_exists('USERS_DB_URL')}"

ENGINE = create_async_engine(database_url, echo=enable_debug_logging())


async def create_db_and_tables():
    async with ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with AsyncSession(ENGINE) as session:
        yield session


UsersSessionDep = Annotated[AsyncSession, Depends(get_session)]
