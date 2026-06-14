from dataclasses import dataclass
from uuid import uuid4


@dataclass
class Task:
    id: str
    text: str
    completed: bool = False

    @classmethod
    def create(cls, text: str) -> "Task":
        return cls(id=uuid4().hex, text=text.strip())
