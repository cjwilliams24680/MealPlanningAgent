from dataclasses import dataclass, field
from typing import Any


@dataclass
class Conversation:
    id: str
    user_id: str
    history: list[Any] = field(default_factory=list)
