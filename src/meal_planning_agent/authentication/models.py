from sqlmodel import Field, SQLModel


# TODO replace this placeholder with JWT
class AuthSessionBase(SQLModel):
    session_token: str = Field(
        description="A non-expiring session token. Will be replaced later when I add real auth."
    )
    user_id: str = Field(description="The user who this session belongs to.")


class AuthSession(AuthSessionBase, table=True):
    __tablename__: str = "sessions"

    id: int | None = Field(default=None, primary_key=True)
