from typing import List

from .tagset import Tagset


class PronounTagset(Tagset):
    def __init__(self, pos: str, grammemes: List[str]):
        super().__init__(pos)

        self.person = grammemes[1]
        self.case = grammemes[2].split("/")[-1]
        self.number = grammemes[3].split("/")[-1] if self.person != "возвр" else "ед"

    def __str__(self):
        return ";".join([self.person, self.case, self.number])
