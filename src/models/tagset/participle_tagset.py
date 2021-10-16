from typing import List

from utils import replace_chars
from utils.characters import cyrillic_lowercase_homoglyphs, latin_lowercase_homoglyphs

from .tagset import Tagset


class ParticipleTagset(Tagset):
    def __init__(self, pos: str, grammemes: List[str]):
        super().__init__(pos)

        # Additonal property
        self.is_reflexive = self.pos.endswith("/в")

        declension = replace_chars(
            grammemes[0], cyrillic_lowercase_homoglyphs, latin_lowercase_homoglyphs
        )
        if "/" in declension:
            self.declension = declension.split("/")
        else:
            self.declension = [declension, declension]

        self.tense = grammemes[1]
        self.case = grammemes[2].split("/")[-1]
        self.number = grammemes[3].split("/")[-1]
        self.gender = grammemes[4].split("/")[-1] if grammemes[4] != "0" else "м"

        # Additional property
        self.voice = "пас" if self.declension[0] in ("a", "o", "тв") else "акт"

    def __str__(self):
        return ";".join(
            [self.declension[1], self.tense, self.case, self.number, self.gender]
        )
