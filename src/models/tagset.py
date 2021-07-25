import re
from typing import List, Optional, Tuple


from utils.characters import latin_lowercase_homoglyphs, cyrillic_lowercase_homoglyphs
from utils import replace_chars


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

    @staticmethod
    def factory(columns: List[str]):
        pos = replace_chars(
            columns[0], latin_lowercase_homoglyphs, cyrillic_lowercase_homoglyphs
        )

        # Ignore ambiguous part of speech
        if "/" in pos and not re.search(r"/([внп]|ср)$", pos):
            pos = pos.split("/")[-1]

        if pos in ("сущ", "прил", "прил/ср", "числ", "числ/п"):
            return NounTagset(pos, columns[1:])
        if pos == "мест":
            return (
                PronounTagset(pos, columns[1:])
                if columns[1] == "личн"
                else NounTagset(pos, columns[1:])
            )
        if pos in ("гл", "гл/в"):
            return VerbTagset(pos, columns[1:])
        if pos in ("прич", "прич/в"):
            return ParticipleTagset(pos, columns[1:])

        return Tagset(pos)


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


class PronounTagset(Tagset):
    def __init__(self, pos: str, grammemes: List[str]):
        super().__init__(pos)

        self.person = grammemes[1]
        self.case = grammemes[2].split("/")[-1]
        self.number = grammemes[3].split("/")[-1] if self.person != "возвр" else "ед"

    def __str__(self):
        return ";".join([self.person, self.case, self.number])


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
