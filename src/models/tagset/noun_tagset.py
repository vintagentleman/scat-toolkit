from typing import List

from utils import replace_chars
from utils.characters import cyrillic_lowercase_homoglyphs, latin_lowercase_homoglyphs

from .tagset import Tagset


class NounTagset(Tagset):
    def __init__(self, pos: str, grammemes: List[str]):
        super().__init__(pos)

        # Save both the etymologic and morphological declension type
        declension = (
            grammemes[0]
            if self.pos == "мест"
            else replace_chars(
                grammemes[0], cyrillic_lowercase_homoglyphs, latin_lowercase_homoglyphs
            )
        )
        if "/" in declension:
            if declension.count("/") > 1:
                if declension.startswith("р/скл"):
                    self.declension = declension.rsplit("/", 1)
                else:
                    self.declension = declension.split("/", 1)
            elif declension == "р/скл":
                self.declension = [declension, declension]
            else:
                self.declension = declension.split("/")
        else:
            self.declension = [declension, declension]

        # Save the factual case only
        self.case = grammemes[1].split("/")[-1]

        # Additional property
        self.is_plurale_tantum = grammemes[2] == "pt"
        if self.is_plurale_tantum:
            self.number = "мн"
        else:
            self.number = grammemes[2].split("/")[-1] if grammemes[2] != "0" else "ед"

        self.gender = grammemes[3].split("/")[-1] if grammemes[3] != "0" else "м"

        # Additional property for morphonological notes
        self.note = grammemes[4]

    def is_reduced(self) -> bool:
        # fmt: off
        return (
            self.declension[1] in ("a", "ja")
            and (self.case, self.number) == ("род", "мн")
            or
            self.declension[1] in ("o", "jo")
            and self.gender == "м"
            and (self.case, self.number) not in (("им", "ед"), ("вин", "ед"), ("род", "мн"))
            or
            self.declension[1] in ("o", "jo")
            and self.gender == "ср"
            and (self.case, self.number) == ("род", "мн")
            or
            self.declension[1] in ("i", "u")
            and (self.case, self.number) not in (("им", "ед"), ("вин", "ед"))
            or
            self.declension[1].startswith("e")
            and (self.case, self.number) not in (("им", "ед"), ("вин", "ед"), ("род", "мн"))
            or
            self.declension[1] == "uu"
            and (self.case, self.number) not in (("им", "ед"), ("вин", "ед"), ("род", "мн"))
        )
        # fmt: on

    def __str__(self):
        return ";".join([self.declension[1], self.case, self.number, self.gender])
