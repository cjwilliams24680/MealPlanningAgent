import uuid
from dataclasses import dataclass


def create_session() -> str:
    return str(uuid.uuid4())

@dataclass
class UserMetadata:
    session_id: str
