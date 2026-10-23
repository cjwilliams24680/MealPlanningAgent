from sqlmodel import Field, SQLModel


# Unused for now, but will be needed later when I add auth
class UserBase(SQLModel):
    email: str = ""


class User(UserBase, table=True):
    __tablename__: str = "users"

    id: int | None = Field(default=None, primary_key=True)
