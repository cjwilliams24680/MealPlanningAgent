# ruff: noqa: F401
# pyright: reportUnusedImport=false
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

import meal_planning_agent.preferences.models
from meal_planning_agent.utils import assert_key_exists, enable_debug_logging

database_url = f"postgresql://{assert_key_exists('USERS_DB_URL')}"

ENGINE = create_engine(database_url, echo=enable_debug_logging())


def create_db_and_tables():
    SQLModel.metadata.create_all(ENGINE)


def get_session():
    with Session(ENGINE) as session:
        yield session


UsersSessionDep = Annotated[Session, Depends(get_session)]
