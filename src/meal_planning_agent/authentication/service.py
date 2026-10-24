import uuid

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

import meal_planning_agent.users.service as UserService
from meal_planning_agent.authentication.models import AuthSession
from meal_planning_agent.users.models import (
    User,
)
from meal_planning_agent.users_database import ENGINE


async def create_anonymous_session() -> AuthSession:
    async with AsyncSession(ENGINE) as session:
        user = await UserService.create_user(session)
        session_token = str(uuid.uuid4())
        auth_session = AuthSession(session_token=session_token, user_id=user.id)
        session.add(auth_session)
        await session.commit()
        await session.refresh(auth_session)
        return auth_session


async def is_valid(session_token: str) -> bool:
    if not session_token:
        return False

    async with AsyncSession(ENGINE) as db_session:
        session = await _get_session(session=db_session, session_token=session_token)
        return session is not None


async def get_user(session_token: str) -> User | None:
    async with AsyncSession(ENGINE) as session:
        auth_session = await _get_session(session=session, session_token=session_token)
        if not auth_session:
            return None

        user = await UserService.get_user(session, auth_session.user_id)
        return user


async def _get_session(session: AsyncSession, session_token: str) -> AuthSession | None:
    statement = select(AuthSession).where(
        col(AuthSession.session_token) == session_token
    )
    result = await session.exec(statement)
    sessions = result.all()

    return sessions[0] if sessions else None
