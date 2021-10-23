import re
from typing import Optional

from models.tagset import NounTagset
from models.word import Word
from utils import characters

from .lib import infl
from .noun_lemmatizer import NounLemmatizer


class AdjectiveLemmatizer(NounLemmatizer):
    @staticmethod
    def _remove_comparative_suffix(stem: str, tagset: NounTagset) -> str:
        if (tagset.case, tagset.number, tagset.gender) in (
            ("им", "ед", "м"),
            ("им", "ед", "ср"),
        ):
            return stem
        if (suffix := re.search("[ИЪЬ]?Ш$", stem)) is not None:
            return stem[: -len(suffix.group())]
        return stem

    @staticmethod
    def get_suffix(stem: str, tagset: NounTagset) -> str:
        if tagset.declension[0] in ("a", "o", "тв"):
            return "ИИ" if stem.endswith(characters.palatalized_consonants) else "ЫИ"
        return "И" if stem.endswith(characters.vowels) else "ИИ"

    @classmethod
    def lemmatize(cls, word: Word) -> Optional[str]:
        norm = word.norm if word.norm.endswith(characters.vowels) else f"{word.norm}`"
        tagset = word.tagset

        # Стемминг
        stem = cls.get_stem(
            norm,
            (tagset.declension[1], tagset.case, tagset.number, tagset.gender),
            infl.noun if tagset.declension[0] not in ("м", "тв") else infl.pronoun,
        )

        if stem is None:
            return None

        # Суффиксы сравнительной степени
        if word.pos == "прил/ср":
            stem = cls._remove_comparative_suffix(stem, tagset)

        # Проверка морфонологических помет
        stem = cls.modify_stem_by_note(stem, tagset.note)

        # Вторая палатализация
        if "*" in tagset.note and stem[-1] in "ЦЗСТ":
            stem = stem[:-1] + characters.palatalization_2[stem[-1]]

        # Удаление прояснённых редуцированных
        if "-о" in tagset.note or "-е" in tagset.note:
            stem = stem[:-2] + stem[-1]

        if stem.endswith("#"):
            stem = stem.rstrip("#") + "-"

        # Нахождение флексии
        if word.is_proper and tagset.declension[0] not in ("м", "тв"):
            return stem + NounLemmatizer.get_suffix(stem, tagset)
        return stem + cls.get_suffix(stem, tagset)
