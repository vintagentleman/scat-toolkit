import re
from typing import List

from models.tagset import NounTagset, ParticipleTagset, PronounTagset, VerbTagset
from models.word import Word


class Pickler:
    AUXILIARY_VERBS = ("НАЧАТИ", "ХОТ+ТИ", "ИМ+ТИ")

    @classmethod
    def pickle(cls, word: Word) -> List[str]:
        ts = word.tagset  # Checked for None in writer module

        if isinstance(ts, NounTagset):
            return [ts.pos, ts.declension[0], ts.case, ts.number, ts.gender]

        if isinstance(ts, ParticipleTagset):
            return [ts.pos, ts.declension[0], ts.tense, ts.case, ts.number, ts.gender]

        if isinstance(ts, PronounTagset):
            return [ts.pos, "личн", ts.person, ts.case, ts.number]

        if isinstance(ts, VerbTagset):
            class_ = ts.cls if ts.cls is not None else ""

            if ts.mood == "повел":
                return [ts.pos, ts.mood, ts.person, ts.number, class_]

            # We can guarantee that mood is subjunctive only for auxiliaries.
            if ts.mood == "сосл" and ts.person is not None:
                return [ts.pos, ts.mood, ts.person, ts.number]

            # Here we omit mood and tense, b/c it can be either ind./subj. and imp./pqp. respectively.
            # Note that this column order is WRONG for subjunctive, but since it's much rarer, we let that slide...
            if ts.gender is not None:
                return [ts.pos, "", "", ts.gender, ts.number, class_]

            if (
                ts.tense is not None
                and re.match(r"(н/б|буд ?1)", ts.tense)
                and word.lemma in cls.AUXILIARY_VERBS
            ):
                return [ts.pos, ts.mood, "", ts.person, ts.number, class_]

            return [
                ts.pos,
                ts.mood,
                ts.tense if ts.tense is not None else "",
                ts.person,
                ts.number,
                class_,
            ]

        return [ts.pos]
