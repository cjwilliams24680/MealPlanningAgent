from sqlmodel.ext.asyncio.session import AsyncSession

from meal_planning_agent.users.models import (
    User,
)


async def create_user(session: AsyncSession) -> User:
    user = User()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)
