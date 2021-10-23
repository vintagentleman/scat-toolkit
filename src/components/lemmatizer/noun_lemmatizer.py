import re
from typing import Optional, Tuple

from models.tagset import NounTagset
from models.word import Word
from utils import characters

from .lemmatizer import Lemmatizer
from .lib import infl, specials


class NounLemmatizer(Lemmatizer):
    @classmethod
    def _modify_stem(cls, stem: str, tagset: NounTagset) -> str:
        def __remove_suffix(s: str, decl: Tuple[str, str]) -> str:
            for theme in specials.noun_them_suff:
                if theme in decl:
                    if (
                        suffix := re.search(specials.noun_them_suff[theme], s)
                    ) is not None:
                        return s[: -len(suffix.group())]
            return s

        def __add_suffix(s: str, decl: Tuple[str, str]) -> str:
            if decl[0] == "en" and not (
                s.endswith("ЕН") or re.match("Д[ЪЬ]?Н", s) is not None
            ):
                if (
                    suffix := re.search(specials.noun_them_suff[decl[0]], s)
                ) is not None:
                    s = s[: -len(suffix.group())]
                s += "ЕН"

            elif decl[0] == "uu" and not s.endswith("ОВ"):
                if (
                    suffix := re.search(specials.noun_them_suff[decl[0]], s)
                ) is not None:
                    s = s[: -len(suffix.group())]
                s += "ОВ"

            return s

        # Удаление тематических суффиксов
        if {tagset.declension[0], tagset.declension[1]} & {"ent", "men", "es", "er"}:
            stem = __remove_suffix(stem, tagset.declension)
        # Добавление тематических суффиксов
        elif tagset.declension[0] in ("en", "uu"):
            stem = __add_suffix(stem, tagset.declension)

        # Проверка морфонологических помет
        stem = cls.modify_stem_by_note(stem, tagset.note)

        if stem == "ХРИСТ":
            stem += "ОС"

        # Для слова 'БРАТЪ' во мн. ч. - минус Ь или И
        if tagset.declension == ["o", "ja"]:
            stem = stem[:-1]

        # Для гетероклитик на -ин- во мн. ч.
        if tagset.declension == ["o", "en"] and not stem.endswith(("АР", "ТЕЛ")):
            stem += "ИН"

        return stem

    @staticmethod
    def modify_stem_by_note(stem: str, note: str) -> str:
        note = re.sub(r"[+-][ое]", "", note)

        if "+" in note:
            stem += note[note.index("+") + 1 :].upper()
        elif "-" in note:
            stem = stem[: -len(note[note.index("-") + 1 :])]

        return stem

    @staticmethod
    def _de_reduce_stem(stem: str, tagset: NounTagset) -> str:
        if tagset.declension[0] == "ja" and stem[-2] == "Е":
            return stem[:-2] + stem[-1]
        if tagset.declension[0] == "jo" and stem[-2] in characters.consonants:
            return stem[:-1] + "Е" + stem[-1]
        return stem

    @staticmethod
    def _de_reduce_stem_by_note(stem: str, note: str) -> str:
        if "+о" in note:
            return stem[:-1] + "О" + stem[-1]
        if "+е" in note:
            return stem[:-1] + "Е" + stem[-1]
        return stem[:-2] + stem[-1]

    @staticmethod
    def _check_grd(stem: str) -> Tuple[Optional[str], str]:
        if (match := re.search("(ГРАД|ГОРОД)$", stem)) is not None:
            return match.group(), stem[: match.start()]
        return None, stem

    @staticmethod
    def get_suffix(stem: str, tagset: NounTagset) -> str:
        if not tagset.is_plurale_tantum:
            if tagset.declension[0] == "a":
                return "А"
            if tagset.declension[0] == "ja":
                return "А" if stem.endswith(characters.hush_consonants) else "Я"
            if tagset.declension[0] == "o":
                return "Ъ" if tagset.gender == "м" else "О"
            if tagset.declension[0] == "jo":
                if tagset.gender == "м":
                    return (
                        "Ь"
                        if stem.endswith(
                            characters.soft_consonants + characters.hush_consonants
                        )
                        else "И"
                    )
                return "Е"
            if tagset.declension[0] == "u":
                return "Ъ"
            if tagset.declension[0] == "i":
                return "Ь"
            if tagset.declension[0] == "en":
                return "Ь"
            if tagset.declension[0] == "men":
                return "Я"
            if tagset.declension[0] == "ent":
                return "А" if stem.endswith(characters.hush_consonants) else "Я"
            if tagset.declension[0] == "er":
                return "И"
            if tagset.declension[0] == "es":
                return "О"
            return "Ь"
        else:
            if tagset.declension[0] == "a":
                return "Ы"
            if tagset.declension[0] == "o":
                return "А"
            if tagset.gender == "м":
                return "ИЕ"
            return "И"

    @classmethod
    def lemmatize(cls, word: Word) -> Optional[str]:
        # Добавление номинального гласного
        norm = word.norm if word.norm.endswith(characters.vowels) else f"{word.norm}`"
        tagset = word.tagset

        # Проверка исключительных случаев
        for key in specials.noun:
            if re.match(key, norm) is not None:
                return specials.noun[key]

        # Стемминг (с учётом особого смешения)
        if tagset.declension[1] in ("a", "ja", "i") and tagset.gender == "ср":
            stem = cls.get_stem(
                norm, (tagset.declension[1], tagset.case, tagset.number, "м"), infl.noun
            )
        else:
            stem = cls.get_stem(
                norm,
                (tagset.declension[1], tagset.case, tagset.number, tagset.gender),
                infl.noun,
            )

        if stem is None:
            return None

        # Проверка на склоняемость второй части
        if word.is_proper:
            grd, stem = cls._check_grd(stem)

            if grd is not None:
                stem = cls.get_stem(
                    stem,
                    (tagset.declension[1], tagset.case, tagset.number, tagset.gender),
                    infl.noun,
                )

            if stem is None:
                return None
        else:
            grd = None

        # Модификации по типам склонения и другие
        stem = cls._modify_stem(stem, tagset)

        # Первая палатализация
        if stem[-1] in "ЧЖШ" and (
            (tagset.case, tagset.number, tagset.gender) == ("зв", "ед", "м")
            or stem in ("ОЧ", "УШ")
        ):
            if tagset.declension == ["jo", "o"]:
                stem = stem[:-1] + characters.soft_palatalization_1[stem[-1]]
            else:
                stem = stem[:-1] + characters.palatalization_1[stem[-1]]

        # Вторая палатализация
        elif "*" in tagset.note and stem[-1] in "ЦЗСТ":
            stem = stem[:-1] + characters.palatalization_2[stem[-1]]

        # Прояснение/исчезновение редуцированных
        if any(note in tagset.note for note in ("+о", "+е", "-о", "-е")):
            stem = cls._de_reduce_stem_by_note(stem, tagset.note)
        elif stem[-1] == "Ц" and tagset.is_reduced():
            stem = cls._de_reduce_stem(stem, tagset)

        # 'НОВЪ' --> 'НОВГОРОДЪ'; 'ЦАРЬ' --> 'ЦАРГРАДЪ' (?)
        if grd is not None:
            stem += grd

        # Нахождение флексии
        return stem + cls.get_suffix(stem, tagset)
