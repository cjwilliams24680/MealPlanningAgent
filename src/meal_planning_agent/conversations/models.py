from dataclasses import dataclass

from agents import SQLiteSession


@dataclass
class Conversation:
    id: str
    user_id: str
    history: SQLiteSession
