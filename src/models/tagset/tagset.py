from typing import Optional, Tuple


class Tagset:
    def __init__(self, pos: str):
        self.pos: str = pos

        self.declension: Optional[Tuple[str, str]] = None
        self.case: Optional[str] = None
        self.number: Optional[str] = None
        self.gender: Optional[str] = None

        self.person: Optional[str] = None

        self.mood: Optional[str] = None
        self.tense: Optional[str] = None
        self.role: Optional[str] = None
        self.cls: Optional[str] = None

        self.note: Optional[str] = None
