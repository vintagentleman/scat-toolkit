import re
from typing import Optional

from models.tagset import NounTagset
from models.word import Word
from utils import characters

from .adjective_lemmatizer import AdjectiveLemmatizer
from .lib import infl, specials


class NumeralLemmatizer(AdjectiveLemmatizer):
    @staticmethod
    def _modify_pronoun(stem: str) -> str:
        if re.match("В[ЪЬ]?С$", stem):
            return "ВЕС"
        if re.match("В[ЪЬ]?Ш$", stem):
            return "ВАШ"
        if re.match("Н[ЪЬ]?Ш$", stem):
            return "НАШ"
        if re.match("(К|ОБ|М|СВ|Т|ТВ)О$", stem):
            return stem[:-1]
        if stem in ("С", "СИ"):
            return "СЕ"
        if stem == "Н":
            return ""
        return stem

    @staticmethod
    def _add_neg(stem: str, neg: Optional[re.Match], zhe: Optional[re.Match]) -> str:
        if neg is not None:  # Префикс стандартный
            return neg.group() + stem
        if stem in ("КТО", "ЧТО") and zhe is not None:  # Префикс отсечён предлогом
            return "НИ" + stem
        return stem

    @staticmethod
    def _add_zhe(zhe: Optional[re.Match], suffix: str = "") -> str:
        return suffix if zhe is None else suffix + zhe.group()

    @staticmethod
    def get_suffix(stem: str, tagset: NounTagset) -> str:
        if tagset.declension[0] in ("тв", "м"):
            if stem.startswith("ЕДИН"):
                return "Ъ"
            elif re.match("(Д[ЪЬ]?В|ОБ)$", stem):
                return "А"
            # Собирательные числительные и нумерализованные прилагательные
            return "Е" if stem.endswith(characters.vowels) else "О"
        else:
            if stem.startswith("ТР"):
                return "И"
            elif stem.startswith("ЧЕТЫР"):
                return "Е"
            return AdjectiveLemmatizer.get_suffix(stem, tagset)

    @classmethod
    def lemmatize(cls, word: Word) -> Optional[str]:
        norm = word.norm if word.norm.endswith(characters.vowels) else f"{word.norm}`"
        tagset = word.tagset

        # Обработка НЕ- и -ЖЕ/-ЖДО
        neg, zhe = None, None

        if word.pos == "мест":
            if (zhe := re.search("ЖЕ$|Ж[ЪЬ]?Д[ЕО]$", norm)) is not None:
                norm = norm[: -len(zhe.group())]
            if (neg := re.match("Н[+ЕИ](?=[КЧ])", norm)) is not None:
                norm = norm[len(neg.group()) :]

        if not norm.endswith(characters.vowels):
            norm = f"{word.norm}`"  # Добавление номинального гласного

        if word.pos == "мест":
            # Проверка исключительных случаев
            if re.match("К[ОЪ]$", norm) and zhe is not None and "Д" in zhe.group():
                return cls._add_neg("КО", neg, zhe) + cls._add_zhe(zhe)
            # Проверка вопросительных местоимений
            if (tagset.declension[0], tagset.case) in infl.pron_interr and re.match(
                infl.pron_interr[(tagset.declension[0], tagset.case)][0], norm
            ):
                if zhe is not None and "Д" in zhe.group():
                    return cls._add_neg("КО", neg, zhe) + cls._add_zhe(zhe)
                return cls._add_neg(
                    infl.pron_interr[(tagset.declension[0], tagset.case)][1], neg, zhe
                ) + cls._add_zhe(zhe)
        else:
            # Проверка на изменяемость обеих частей
            for key in specials.numeral:
                if re.match(key, norm) is not None:
                    return specials.numeral[key]

        if tagset.declension[0] != "р/скл":
            # Сначала ищем в местоименной парадигме
            stem = cls.get_stem(
                norm,
                (tagset.declension[1], tagset.case, tagset.number, tagset.gender),
                infl.pronoun,
            )

            # Если не нашли, то обращаемся к именной (актуально прежде всего для им. и вин. п.)
            if stem is None:
                if tagset.declension[1] == "тв":
                    stem = cls.get_stem(
                        norm,
                        (
                            "o" if tagset.gender in ("м", "ср") else "a",
                            tagset.case,
                            tagset.number,
                            tagset.gender,
                        ),
                        infl.noun,
                    )
                elif tagset.declension[1] == "м":
                    stem = cls.get_stem(
                        norm,
                        (
                            "jo" if tagset.gender in ("м", "ср") else "ja",
                            tagset.case,
                            tagset.number,
                            tagset.gender,
                        ),
                        infl.noun,
                    )
                else:
                    stem = cls.get_stem(
                        norm,
                        (
                            tagset.declension[1],
                            tagset.case,
                            tagset.number,
                            "м"
                            if tagset.declension[1] in ("a", "ja", "i")
                            and tagset.gender == "ср"
                            else tagset.gender,
                        ),
                        infl.noun,
                    )
        else:
            stem = cls.get_stem(
                norm,
                (
                    "тв"
                    if (tagset.case, tagset.number, tagset.gender)
                    in (("тв", "ед", "м"), ("тв", "ед", "ср"))
                    or tagset.number == "мн"
                    else "м",
                    tagset.case,
                    tagset.number,
                    tagset.gender,
                ),
                infl.pronoun,
            )

            if stem is None:
                stem = cls.get_stem(
                    norm,
                    (
                        "jo" if tagset.gender in ("м", "ср") else "ja",
                        tagset.case,
                        tagset.number,
                        tagset.gender,
                    ),
                    infl.noun,
                )

        # Обработка основы
        if stem is None:
            return None

        # Модификация основы
        stem = cls._modify_pronoun(stem)

        # Проверка морфонологических помет
        stem = cls.modify_stem_by_note(stem, tagset.note)

        # Вторая палатализация
        if "*" in tagset.note and stem[-1] in "ЦЗСТ":
            stem = stem[:-1] + characters.palatalization_2[stem[-1]]

        # Нахождение флексии
        if word.pos == "мест":
            suffix = (
                specials.pronoun[stem]
                if stem in specials.pronoun
                else AdjectiveLemmatizer.get_suffix(stem, tagset)
            )
        else:
            suffix = cls.get_suffix(stem, tagset)

        return cls._add_neg(stem, neg, zhe) + cls._add_zhe(zhe, suffix)
