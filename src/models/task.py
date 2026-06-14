from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Task:
    id: str
    text: str
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    @classmethod
    def create(cls, text: str) -> "Task":
        return cls(id=uuid4().hex, text=text.strip())
