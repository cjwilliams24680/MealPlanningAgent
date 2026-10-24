from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

import meal_planning_agent.users.service as UsersService
from meal_planning_agent.preferences.models import (
    UserPreferences,
    UserPreferencesBase,
)
from meal_planning_agent.users_database import ENGINE


async def get_or_create_preferences(user_id: int) -> UserPreferences:
    if not user_id:
        raise ValueError("Invalid user id was passed")

    async with AsyncSession(ENGINE) as session:
        return await _get_or_create_preferences(session=session, user_id=user_id)


async def upsert_preferences(
    preferences_update: UserPreferencesBase,
    user_id: int,
):
    if not user_id:
        raise ValueError("Invalid user id was passed")

    async with AsyncSession(ENGINE) as session:
        preferences = await _get_or_create_preferences(session=session, user_id=user_id)
        update = preferences_update.model_dump()
        preferences.sqlmodel_update(update)
        session.add(preferences)
        await session.commit()


async def _get_preferences(
    session: AsyncSession, user_id: int
) -> UserPreferences | None:
    statement = select(UserPreferences).where(col(UserPreferences.user_id) == user_id)
    result = await session.exec(statement)
    preferences = result.all()

    return preferences[0] if preferences else None


async def _get_or_create_preferences(
    session: AsyncSession, user_id: int
) -> UserPreferences:
    existing_preferences = await _get_preferences(session=session, user_id=user_id)

    if existing_preferences:
        return existing_preferences

    user = await UsersService.get_user(session=session, user_id=user_id)
    if user is None:
        raise ValueError("User does not exist")

    new_preferences = UserPreferences(user_id=user_id)
    session.add(new_preferences)
    await session.commit()
    await session.refresh(new_preferences)

    return new_preferences
