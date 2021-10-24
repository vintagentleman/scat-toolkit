from models.row import Row
from models.tagset.pronoun_tagset import PronounTagset

from lxml import etree


class PToken:
    def __init__(self, row: Row):
        self._word = row.word  # Checked for None in writer module
        self.form = str(self._word)
        self.lemma = (
            self._word.lemma.replace("+", "Ѣ").lower()
            if self._word.lemma is not None
            else None
        )

        self.presentation_before = (
            row.head_punctuation.source if row.head_punctuation is not None else None
        )
        self.presentation_after = (
            f"{row.tail_punctuation.source} "
            if row.tail_punctuation is not None
            else " "
        )

    def xml(self) -> etree.Element:
        token = etree.Element("token")
        token.set("form", self.form)

        if self._word.pos is not None:
            token.set("part-of-speech", self.part_of_speech)
            token.set("morphology", self.morphology)
        if self.lemma is not None:
            token.set("lemma", self.lemma)

        if self.presentation_before is not None:
            token.set("presentation-before", self.presentation_before)
        token.set("presentation-after", self.presentation_after)

        return token

    @property
    def part_of_speech(self) -> str:
        if self._word.pos == "сущ":
            # Unfortunately, the PROIEL spec does not support
            # animacy for other parts of speech e.g. adjectives
            return "Ne" if "*" in self._word.source else "Nb"

        if self._word.pos == "мест":
            # SCAT does not support a more fine-grained distinction
            # other than personal, reflexive, and everything else
            if isinstance(self._word.tagset, PronounTagset):
                return "Pk" if self._word.tagset.person == "возвр" else "Pp"
            return "Px"

        if self._word.pos.startswith("прил"):
            return "A-"

        if self._word.pos.startswith("числ"):
            return "Mo" if self._word.pos == "числ/п" else "Ma"

        # Verbal distinctions are encoded in the mood property
        if self._word.pos.startswith(("гл", "прич", "инф", "суп")):
            return "V-"

        if self._word.pos == "нар":
            return "Df"

        # PROIEL does not discern between pre- and postpositions
        if self._word.pos in ("пред", "посл"):
            return "R-"

        if self._word.pos == "союз":
            return "C-"

        if self._word.pos == "част":
            return "G-"

        if self._word.pos == "межд":
            return "I-"

        if self._word.pos.isnumeric():
            return "Ma"

        return "X-"

    @property
    def morphology(self) -> str:
        return "".join(
            [
                self._person(),
                self._number(),
                self._tense(),
                self._mood(),
                self._voice(),
                self._gender(),
                self._case(),
                self._degree(),
                self._strength(),
                self._inflection(),
            ]
        )

    def _person(self) -> str:
        if self._word.tagset.person is None or self._word.tagset.person == "возвр":
            return "-"
        if self._word.tagset.person in ("1", "2", "3"):
            return self._word.tagset.person
        return "x"

    def _number(self) -> str:
        if self._word.tagset.number is None or self._word.tagset.person == "возвр":
            return "-"
        if self._word.tagset.number == "ед":
            return "s"
        if self._word.tagset.number == "мн":
            return "p"
        if self._word.tagset.number == "дв":
            return "d"
        return "x"

    def _tense(self) -> str:
        if self._word.tagset.tense is None:
            return "-"
        if self._word.tagset.tense in ("н/б", "наст"):
            return "p"
        if self._word.tagset.tense.startswith(("аор", "а/имп")):
            return "a"
        if self._word.tagset.tense == "имп":
            return "i"
        if self._word.tagset.tense == "плюскв":
            return "l"
        if self._word.tagset.tense == "перф":
            return "r"
        if self._word.tagset.tense in ("буд", "буд 1"):
            return "f"
        if self._word.tagset.tense == "буд 2":
            return "t"
        if self._word.tagset.tense == "прош":
            return "u"
        return "x"

    def _mood(self) -> str:
        if self._word.pos.startswith("прич"):
            return "p"
        if self._word.pos.startswith("инф"):
            return "n"
        if self._word.pos == "суп":
            return "u"

        if self._word.tagset.mood is None:
            return "-"
        if self._word.tagset.mood == "изъяв":
            return "i"
        if self._word.tagset.mood == "повел":
            return "m"
        if self._word.tagset.mood == "сосл":
            return "s"
        return "x"

    def _voice(self) -> str:
        if not self._word.pos.startswith(("гл", "прич", "инф")):
            return "-"
        if self._word.pos.endswith("/в"):
            return "p"
        if (
            self._word.pos == "прич"
            and self._word.tagset.declension is not None
            and self._word.tagset.declension[0] in ("a", "o", "тв")
        ):
            return "p"
        return "a"  # Note active voice by default

    def _gender(self) -> str:
        if self._word.tagset.gender is None or (
            self._word.pos.startswith("гл") and self._word.tagset.mood != "сосл"
        ):
            return "-"
        if self._word.tagset.gender == "м":
            return "m"
        if self._word.tagset.gender == "ж":
            return "f"
        if self._word.tagset.gender == "ср":
            return "n"
        return "x"

    def _case(self) -> str:
        if self._word.tagset.case is None:
            return "-"
        if self._word.tagset.case == "им":
            return "n"
        if self._word.tagset.case == "род":
            return "g"
        if self._word.tagset.case == "дат":
            return "d"
        if self._word.tagset.case == "вин":
            return "a"
        if self._word.tagset.case == "тв":
            return "i"
        if self._word.tagset.case == "мест":
            return "l"
        if self._word.tagset.case == "зв":
            return "v"
        return "x"

    def _degree(self) -> str:
        if not self._word.pos.startswith("прил") or self._word.pos == "прил/н":
            return "-"
        return "c" if self._word.pos == "прил/ср" else "p"

    def _strength(self) -> str:
        if (
            not self._word.pos.startswith(("прил", "прич"))
            or self._word.pos == "прил/н"
        ):
            return "-"
        if self._word.tagset.declension is not None:
            return "s" if self._word.tagset.declension[1] in ("тв", "м") else "w"
        return "t"

    def _inflection(self) -> str:
        return (
            "i"
            if self._word.pos.startswith(
                ("сущ", "мест", "прил", "числ", "гл", "прич", "инф", "суп")
            )
            and self._word.pos != "прил/н"
            else "n"
        )
