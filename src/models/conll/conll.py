from collections import OrderedDict
from typing import Dict, Optional

import models.conll.lib as lib
from models.punctuation import Punctuation
from models.word import Word


class UToken:
    def __init__(self):
        self.id: int = 0
        self.form: Optional[str] = None
        self.lemma: Optional[str] = None
        self.upos: Optional[str] = None
        self.xpos: Optional[str] = None
        self.feats: Dict[str, str] = {}

        self.head = 0
        self.deprel = None
        self.deps = None
        self.misc = None

    def __str__(self):
        return "\t".join(
            [
                str(self.id),
                self.form if self.form is not None else "_",
                self.lemma if self.lemma is not None else "_",
                self.upos if self.upos is not None else "_",
                self.xpos if self.xpos is not None else "_",
                "|".join([f"{k}={v}" for k, v in self.feats.items()]) if self.feats else "_",
                self.head if self.head != 0 else "_",
                self.deprel if self.deprel is not None else "_",
                self.deps if self.deps is not None else "_",
                self.misc if self.misc is not None else "_",
            ]
        )


class UWord(UToken):
    def __init__(self, word: Word):
        super().__init__()

        self.id = word.id
        self.form = str(word)

        if word.lemma is not None:
            self.lemma = word.lemma.replace("+", "Ѣ").lower()

        self.upos = self.__get_upos(word)
        self.xpos = word.pos
        self.feats = self.__get_feats(word)

        if word.error is not None:
            self.misc = f"CorrectForm={word.source_to_unicode()}"

    @staticmethod
    def __get_upos(word: Word) -> str:
        if word.pos == "сущ":
            return "PROPN" if word.is_proper else "NOUN"
        if word.pos in ("прил", "прил/ср", "прил/н", "числ/п"):
            return "ADJ"
        if word.pos == "числ" or word.is_cardinal_number():
            return "NUM"
        if word.pos == "мест":
            return "PRON"  # TODO Distinguish DET
        if word.pos in ("гл", "гл/в", "прич", "прич/в", "инф", "инф/в", "суп"):
            return "AUX" if word.tagset.role == "св" else "VERB"
        if word.pos == "нар":
            return "ADV"
        if word.pos in ("пред", "посл"):
            return "ADP"
        if word.pos == "союз":
            return "CCONJ"  # TODO Distinguish SCONJ
        if word.pos == "част":
            return "PART"
        if word.pos == "межд":
            return "INTJ"
        return "X"

    @staticmethod
    def __get_feats(word: Word) -> Dict[str, str]:
        feats = OrderedDict()

        if word.tagset.tense == "имп":
            feats["Aspect"] = "Imp"
        elif word.tagset.tense in (
            "аор пр",
            "аор сигм",
            "аор гл",
            "аор нов",
            "а/имп",
            "перф",
            "прош",
            "буд 2",
        ):
            feats["Aspect"] = "Perf"

        if word.tagset.case in lib.cases:
            feats["Case"] = lib.cases[word.tagset.case]

        if word.pos.startswith("прил"):
            feats["Degree"] = "Cmp" if word.pos == "прил/ср" else "Pos"

        if word.tagset.gender in lib.genders:
            feats["Gender"] = lib.genders[word.tagset.gender]

        if word.tagset.mood in lib.moods:
            feats["Mood"] = lib.moods[word.tagset.mood]

        if hasattr(word, "is_plurale_tantum") and word.is_plurale_tantum:
            feats["Number"] = "Ptan"
        elif word.tagset.number in lib.numbers:
            feats["Number"] = lib.numbers[word.tagset.number]

        if word.pos.startswith("числ"):
            feats["NumType"] = "Ord" if word.pos == "числ/п" else "Card"

        if word.tagset.person is not None and word.tagset.person.isnumeric():
            feats["Person"] = word.tagset.person

        if word.pos == "мест" and word.tagset.person is not None:
            feats["PronType"] = "Prs"

        if word.pos.endswith("/в") or word.tagset.person == "возвр":
            feats["Reflex"] = "Yes"

        if word.tagset.tense in lib.tenses:
            feats["Tense"] = lib.tenses[word.tagset.tense]

        if word.error is not None:
            feats["Typo"] = "Yes"

        if word.pos in lib.verb_forms:
            feats["VerbForm"] = lib.verb_forms[word.pos]

        if hasattr(word.tagset, "voice"):
            feats["Voice"] = "Act" if word.tagset.voice == "акт" else "Pass"

        return feats


class UPunctuation(UToken):
    def __init__(self, punct: Punctuation):
        super().__init__()

        self.id = punct.id
        self.form = punct.source
        self.lemma = punct.source
        self.upos = "PUNCT"
