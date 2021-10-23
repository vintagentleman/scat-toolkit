import re
from typing import Optional

from models.word import Word
from utils import characters

from .lemmatizer import Lemmatizer
from .lib import infl


class PronounLemmatizer(Lemmatizer):
    @classmethod
    def lemmatize(cls, word: Word) -> Optional[str]:
        norm = word.norm if word.norm.endswith(characters.vowels) else f"{word.norm}`"
        tagset = word.tagset

        if tagset.person == "возвр" and tagset.case in infl.pron_refl:
            if re.match(infl.pron_refl[tagset.case][0], norm) is not None:
                return infl.pron_refl[tagset.case][1]
            if norm == "С`":
                return "СЕБЕ"
        elif (tagset.person, tagset.case, tagset.number) in infl.pron_pers:
            if (
                re.match(
                    infl.pron_pers[(tagset.person, tagset.case, tagset.number)][0],
                    norm,
                )
                is not None
            ):
                return infl.pron_pers[(tagset.person, tagset.case, tagset.number)][1]
            if norm == "М`":
                return "АЗЪ"
            if norm == "Т`":
                return "ТЫ"

        return None
