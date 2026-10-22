from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from meal_planning_agent.preferences.models import (
    UserPreferences,
    UserPreferencesBase,
)
from meal_planning_agent.users_database import ENGINE


async def get_or_create_preferences_for_user(user_id: str) -> UserPreferencesBase:
    if not user_id:
        raise ValueError("Invalid user id was passed")

    with AsyncSession(ENGINE) as session:
        return await _get_or_create_preferences_for_user(
            session=session, user_id=user_id
        )


async def upsert_preferences(
    preferences_update: UserPreferencesBase,
    user_id: str,
):
    if not user_id:
        raise ValueError("Invalid user id was passed")

    with AsyncSession(ENGINE) as session:
        preferences = _get_or_create_preferences_for_user(session, user_id)
        update = preferences_update.model_dump()
        preferences.sqlmodel_update(update)
        session.add(preferences)
        session.commit()


async def _get_preferences_for_user(
    session: AsyncSession, user_id: int
) -> UserPreferences | None:
    statement = select(UserPreferences).where(col(UserPreferences.user_id) == user_id)
    result = await session.exec(statement)
    preferences = result.all()

    return next(preferences, None)


async def _get_or_create_preferences_for_user(
    session: AsyncSession, user_id: int
) -> UserPreferences:
    existing_preferences = _get_preferences_for_user(session, user_id)

    if existing_preferences:
        return existing_preferences

    # TODO once i finish the user table, do a query here to assert that the user exists before creating a new preference

    new_preferences = UserPreferences(user_id=user_id)
    session.add(new_preferences)
    await session.commit()
    await session.refresh(new_preferences)

    return new_preferences
