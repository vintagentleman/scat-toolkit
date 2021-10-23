from typing import List

from utils import replace_chars
from utils.characters import cyrillic_lowercase_homoglyphs, latin_lowercase_homoglyphs

from .tagset import Tagset


class VerbTagset(Tagset):
    def __init__(self, pos: str, grammemes: List[str]):
        super().__init__(pos)

        # Additonal property
        self.is_reflexive = self.pos.endswith("/в")

        self.mood = replace_chars(
            grammemes[0], latin_lowercase_homoglyphs, cyrillic_lowercase_homoglyphs
        ).replace("изьяв", "изъяв")

        if self.mood == "изъяв":
            self.tense = grammemes[1]
            self.number = grammemes[3].split("/")[-1]

            if grammemes[2].isnumeric():
                self.person = grammemes[2]
            else:
                self.gender = grammemes[2]

            if grammemes[4].split("/")[0].isnumeric():
                self.cls = grammemes[4].split("/")[0]
            else:
                self.role = grammemes[4]
        elif self.mood == "сосл":
            if grammemes[1].isnumeric():
                self.person = grammemes[1]
            else:
                self.gender = grammemes[1]

            self.number = grammemes[2].split("/")[-1]
            self.role = grammemes[3]
        else:
            self.person = grammemes[1]
            self.number = grammemes[2]
            self.cls = grammemes[3].split("/")[0]

    def __str__(self):
        return ";".join(
            grammeme
            for grammeme in [
                self.mood,
                self.tense,
                self.number,
                self.person,
                self.gender,
                self.cls,
                self.role,
            ]
            if grammeme is not None
        )
