import re
from typing import Optional

from models.tagset import VerbTagset
from models.word import Word
from utils import characters, skip_none

from .lemmatizer import Lemmatizer
from .lib import infl, specials, verbs


class VerbLemmatizer(Lemmatizer):
    @staticmethod
    def get_special_verb_stem(stem: str, spec_dict: dict) -> str:
        for regex in spec_dict:
            if (mo := re.match(regex, stem)) is not None:
                return re.sub(regex, mo.group(1) + spec_dict[regex], stem)
        return stem

    @staticmethod
    def get_dictionary_verb_lemma(stem: str, dict_: dict, suffix: str) -> Optional[str]:
        for regex in dict_:
            if (mo := re.match(r"(.*){}$".format(regex), stem)) is not None:
                return (
                    re.sub(r"(.*){}$".format(regex), mo.group(1) + dict_[regex], stem,)
                    + suffix
                )
        return None

    @classmethod
    def get_lemma_with_consonant_stem(cls, stem: str) -> Optional[str]:
        # Подкласс VII/1
        for dict_, suff in [
            (verbs.cls_vii_1, "СТИ"),
            (verbs.cls_vi_2_a, "ТИ"),
            (verbs.cls_vi_1, "ЩИ"),
        ]:
            if (lemma := cls.get_dictionary_verb_lemma(stem, dict_, suff)) is not None:
                return lemma

        # Группа VI/2/б
        if re.search("[МПТ][ЕЬ]?Р$", stem):
            return stem + "+ТИ"

        # Группа VI/2/в
        if re.search("ШИБ$", stem):
            return stem[:-2] + "ИТИ"

        return None

    @staticmethod
    def is_stem_in_dictionary(stem: str, dict_: dict) -> bool:
        return any(re.search(regex + "$", stem) for regex in dict_)

    @staticmethod
    def de_palatalize_stem(stem: str, type_: int) -> str:
        return (
            stem
            if len(stem) == 1
            else stem[:-1]
            + getattr(characters, f"palatalization_{type_}").get(stem[-1], stem[-1])
        )

    @staticmethod
    def modify_jot(stem: str) -> str:
        if stem.endswith(("БЛ", "ВЛ", "МЛ", "ПЛ", "ФЛ")):
            return stem[:-1]

        if stem.endswith(("Ж", "ЖД")):
            stem = stem[:-2] if stem.endswith("ЖД") else stem[:-1]

            for cons in ("Г", "Д", "З", "ЗД"):
                if any(
                    re.search(regex + "$", stem + cons) for regex in verbs.jotted_zh
                ):
                    return stem + cons

        elif stem.endswith(("Ч", "Щ", "ШТ")):
            stem = stem[:-2] if stem.endswith("ШТ") else stem[:-1]

            for cons in ("К", "Т", "СК", "СТ"):
                if any(
                    re.search(regex + "$", stem + cons) for regex in verbs.jotted_tsch
                ):
                    return stem + cons

        elif stem.endswith("Ш") and any(
            re.search(regex + "$", stem[:-1] + "С") for regex in verbs.jotted_sch
        ):
            return stem[:-1] + "С"

        return stem

    @staticmethod
    def modify_uu(stem: str) -> str:
        if stem.endswith("ЖИВ"):
            return stem[:-1]
        if stem.endswith("СЛОВ"):
            return stem + "И"

        if (mo := re.search("[ОЪ]?В$", stem)) is not None:
            stem = stem[: -len(mo.group())]

            if stem[-1] == "З":
                stem += "ВА"
            elif stem[-1] == "Н":
                stem += "У"
            else:
                stem += "Ы"

        return stem

    @classmethod
    def cls_1(cls, stem: str) -> str:
        # Основы на согласный
        if (
            lemma := cls.get_lemma_with_consonant_stem(
                stem[:-1] + characters.palatalization_1.get(stem[-1], stem[-1])
            )
        ) is not None:
            return lemma

        # Чередование /u:/
        stem = cls.modify_uu(stem)

        # Чередование носовых
        if (nasal := re.search(r"[ЕИ]?[МН]$", stem)) is not None:
            stem = stem[: -len(nasal.group())] + (
                "А"
                if stem[: -len(nasal.group())].endswith(characters.hush_consonants)
                else "Я"
            )

        # Основы со вставкой
        elif cls.is_stem_in_dictionary(stem, verbs.cls_vii_2):
            stem = stem[:-1]

        # Приставочные дериваты БЫТИ
        elif stem.endswith("БУД"):
            stem = stem.replace("БУД", "БЫ")

        elif stem.endswith(characters.consonants):
            stem = (
                stem[:-2] + stem[-1] + "А"
                if stem.endswith(verbs.cls_v_1_d)
                else stem + "А"
            )

        return stem + "ТИ"

    @staticmethod
    def cls_2(stem: str) -> str:
        if stem.endswith(verbs.cls_vii_3):
            return stem[:-1] + "ТИ"
        return stem + "УТИ"

    @classmethod
    def cls_3(cls, stem: str) -> str:
        if stem.endswith(characters.vowels):
            if stem.endswith("У"):
                stem = stem[:-1] + (
                    "ЕВА" if stem.endswith(characters.hush_consonants) else "ОВА"
                )
            elif cls.is_stem_in_dictionary(stem, verbs.cls_v_1_b):
                stem += "Я"
            else:
                if (
                    lemma := cls.get_dictionary_verb_lemma(stem, verbs.cls_i_5, "ТИ")
                ) is not None:
                    return lemma
        else:
            # Сочетания с йотом
            if stem.endswith(characters.hush_consonants) or stem.endswith(
                characters.sonorant_consonants
            ):
                stem = cls.modify_jot(stem)

            # Чередование носовых
            if (nasal := re.search(r"[ЕИ]?[МН]$", stem)) is not None:
                stem = stem[: -len(nasal.group())] + (
                    "А"
                    if stem[: -len(nasal.group())].endswith(characters.hush_consonants)
                    else "Я"
                )

            elif cls.is_stem_in_dictionary(stem, verbs.cls_v_2):
                stem = stem[:-2] + "О" + stem[-1] + "О"

            elif cls.is_stem_in_dictionary(stem, verbs.cls_viii):
                stem += "ВА"

            elif stem.endswith(characters.consonants):
                stem += "+" if stem.endswith("ХОТ") else "А"

        return stem + "ТИ"

    @classmethod
    def cls_4(cls, stem) -> str:
        if stem.endswith(characters.hush_consonants) or stem.endswith(
            characters.sonorant_consonants
        ):
            stem = cls.modify_jot(stem)

        if cls.is_stem_in_dictionary(stem, verbs.cls_x_e):
            stem += "+"
        elif cls.is_stem_in_dictionary(stem, verbs.cls_x_a):
            stem += "А" if stem.endswith(characters.hush_consonants) else "Я"
        else:
            stem += "И"

        return stem + "ТИ"

    @staticmethod
    def cls_5(stem: str) -> Optional[str]:
        for regex in verbs.isol:
            if (mo := re.search(r"{}$".format(regex), stem)) is not None:
                return stem[: -len(mo.group())] + verbs.isol[regex] + "ТИ"
        return None

    @classmethod
    def lemmatize(cls, word: Word) -> Optional[str]:
        norm = word.norm
        tagset = word.tagset
        lemma = None

        if tagset.is_reflexive:
            norm = norm[:-2]
        if not norm.endswith(characters.vowels):
            norm = f"{norm}`"

        # Глаголы-связки
        if tagset.role is not None and tagset.role == "св":
            if tagset.mood == "сосл":
                return "AUX-SBJ"
            if tagset.tense == "перф":
                return "AUX-PRF"
            if tagset.tense == "плюскв":
                return "AUX-PQP"

            mo = re.match(r"буд ?([12])", tagset.tense)
            if mo:
                return "AUX-FT" + mo.group(1)
            return None

        if tagset.mood == "изъяв":
            # Простые времена

            if tagset.tense == "н/б":
                # См. Срезневский, т. 1, с. 481
                if (tagset.person, tagset.number) == ("1", "ед") and norm == "В+Д+":
                    lemma = "В+ДАТИ"
                else:
                    lemma = PresentLemmatizer.modify_stem(
                        cls.get_stem(
                            norm, (tagset.person, tagset.number), infl.present,
                        ),
                        tagset,
                    )
            elif tagset.tense == "имп":
                lemma = ImperfectLemmatizer.modify_stem(
                    cls.get_stem(norm, (tagset.person, tagset.number), infl.imperfect,)
                )
            elif tagset.tense == "прош":
                lemma = ElParticipleLemmatizer.modify_stem(
                    cls.get_stem(norm, (tagset.gender, tagset.number), infl.part_el,)
                )
            elif tagset.tense == "аор пр":
                lemma = SimpleAoristLemmatizer.modify_stem(
                    cls.get_stem(
                        norm, (tagset.person, tagset.number), infl.aorist_simple,
                    )
                )
            elif tagset.tense.startswith("аор"):
                # Простейший случай
                if (
                    tagset.tense == "аор гл"
                    and tagset.person in ("2", "3")
                    and tagset.number == "ед"
                ):
                    if (mo := re.search("(?<!\+)С?Т[ЪЬ`]$", norm)) is not None:
                        lemma = norm[: -len(mo.group())] + "ТИ"
                    else:
                        lemma = norm + "ТИ"
                else:
                    lemma = SigmaticAoristLemmatizer.modify_stem(
                        cls.get_stem(
                            norm, (tagset.person, tagset.number), infl.aorist_sigm,
                        ),
                        tagset,
                    )

            elif tagset.tense in ("буд", "а/имп"):
                # Тут лексема одна
                if tagset.tense == "буд":
                    stem = cls.get_stem(
                        norm, (tagset.person, tagset.number), infl.present,
                    )
                else:
                    stem = (
                        norm
                        if tagset.person in ("2", "3") and tagset.number == "ед"
                        else cls.get_stem(
                            norm, (tagset.person, tagset.number), infl.aorist_sigm,
                        )
                    )

                if stem is not None:
                    lemma = "БЫТИ"

            # Сложные времена
            elif re.match("перф|плюскв|буд ?[12]", tagset.tense):
                if tagset.role == "инф":
                    lemma = norm
                if tagset.role is not None and tagset.role.startswith("пр"):
                    lemma = ElParticipleLemmatizer.modify_stem(
                        cls.get_stem(
                            norm, (tagset.gender, tagset.number), infl.part_el,
                        ),
                    )

        elif tagset.mood == "сосл" and (
            tagset.role is not None and tagset.role.startswith("пр")
        ):
            lemma = ElParticipleLemmatizer.modify_stem(
                cls.get_stem(norm, (tagset.gender, tagset.number), infl.part_el,)
            )

        elif tagset.mood == "повел":
            lemma = ImperativeLemmatizer.modify_stem(
                cls.get_stem(norm, (tagset.person, tagset.number), infl.imperative,),
                tagset,
            )

        if lemma is not None and tagset.is_reflexive:
            return f"{lemma}СЯ"
        return lemma


class PresentLemmatizer(VerbLemmatizer):
    @classmethod
    @skip_none
    def modify_stem(
        cls, stem: str, tagset: Optional[VerbTagset] = None
    ) -> Optional[str]:
        # 5 класс
        if tagset.cls == "5" or stem.endswith("БУД"):
            return cls.cls_5(stem)

        # Удаление тематических гласных
        if tagset.mood == "изъяв" and (tagset.person, tagset.number) not in (
            ("1", "ед"),
            ("3", "мн"),
        ):
            stem = stem[:-1]

        try:
            return getattr(cls, "cls_" + tagset.cls)(stem)
        except AttributeError:
            return None


class SimpleAoristLemmatizer(VerbLemmatizer):
    @classmethod
    @skip_none
    def modify_stem(
        cls, stem: str, tagset: Optional[VerbTagset] = None
    ) -> Optional[str]:
        # Основы настоящего времени
        if cls.is_stem_in_dictionary(stem, verbs.cls_vii_2):
            stem = stem[:-1]

        # Первая палатализация
        if stem[-1] in "ЧЖШ":
            stem = cls.de_palatalize_stem(stem, 1)

        # Основы на согласный
        if (lemma := cls.get_lemma_with_consonant_stem(stem)) is not None:
            return lemma

        # 4 класс
        if stem[-1] in characters.consonants or stem in verbs.cls_iv_vow:
            stem += "НУ"

        return stem + "ТИ"


class SigmaticAoristLemmatizer(VerbLemmatizer):
    @classmethod
    @skip_none
    def modify_stem(
        cls, stem: str, tagset: Optional[VerbTagset] = None
    ) -> Optional[str]:
        # Осложнение тематического суффикса
        if tagset.tense == "аор нов" and stem.endswith("О"):
            stem = stem[:-1]

        if tagset.tense == "аор гл":
            return (
                stem[:-2]
                if cls.is_stem_in_dictionary(stem[:-1], verbs.cls_vii_2)
                else stem
            ) + "ТИ"

        # Основы настоящего времени
        if cls.is_stem_in_dictionary(stem, verbs.cls_vii_2):
            stem = stem[:-1]

        # Удлинение корневого гласного
        if tagset.tense == "аор сигм" and stem == "Р+":
            return "РЕЩИ"

        # Основы на согласный
        if (lemma := cls.get_lemma_with_consonant_stem(stem)) is not None:
            return lemma

        # 4 класс
        if stem[-1] in characters.consonants or stem in verbs.cls_iv_vow:
            stem += "НУ"

        return stem + "ТИ"


class ImperfectLemmatizer(VerbLemmatizer):
    @classmethod
    @skip_none
    def modify_stem(
        cls, stem: str, tagset: Optional[VerbTagset] = None
    ) -> Optional[str]:
        # Удаление нестяжённых вокалических сочетаний
        stretch = re.search(r"([+Е][АЯ]|АА|ЯЯ)$", stem)
        if stretch:
            theme = stem[-2]
            stem = stem[:-2]
        else:
            theme = stem[-1]
            stem = stem[:-1]

        # Основы-исключения
        for regex in specials.imperfect:
            if (mo := re.match(regex, stem)) is not None:
                modified_stem = re.sub(
                    regex, mo.group(1) + specials.imperfect[regex], stem,
                )
                if stem != modified_stem:
                    return modified_stem + "ТИ"

        # Основы на согласный
        if (
            lemma := cls.get_lemma_with_consonant_stem(
                stem[:-1] + characters.palatalization_1.get(stem[-1], stem[-1])
            )
        ) is not None:
            return lemma

        # Сочетания с йотом
        if (modified_stem := cls.modify_jot(stem)) != stem:
            return modified_stem + "ИТИ"

        # Второе спряжение
        if cls.is_stem_in_dictionary(stem, verbs.cls_x_e):
            stem += "+"
        elif cls.is_stem_in_dictionary(stem, verbs.cls_x_a):
            stem += "А" if stem.endswith(characters.hush_consonants) else "Я"
        elif cls.is_stem_in_dictionary(stem, verbs.cls_x_i):
            stem += "И"
        # I/5 подкласс
        else:
            if (
                lemma := cls.get_dictionary_verb_lemma(stem, verbs.cls_i_5, "ТИ")
            ) is not None:
                return lemma
            stem += theme

        return stem + "ТИ"


class ElParticipleLemmatizer(VerbLemmatizer):
    @classmethod
    @skip_none
    def modify_stem(
        cls, stem: str, tagset: Optional[VerbTagset] = None
    ) -> Optional[str]:
        # Основы-исключения
        if (modified_stem := cls.get_special_verb_stem(stem, specials.part_el)) != stem:
            return modified_stem + "ТИ"

        # Основы на согласный
        if (lemma := cls.get_lemma_with_consonant_stem(stem)) is not None:
            return lemma

        # 4 класс
        if stem[-1] in characters.consonants or stem in verbs.cls_iv_vow:
            stem += "НУ"

        return stem + "ТИ"


class ImperativeLemmatizer(VerbLemmatizer):
    @classmethod
    @skip_none
    def modify_stem(
        cls, stem: str, tagset: Optional[VerbTagset] = None
    ) -> Optional[str]:
        # Удаление тематических гласных
        if (tagset.person, tagset.number) not in (("2", "ед"), ("3", "ед")):
            stem = stem[:-1]

        # Вторая палатализация
        if (
            lemma := cls.get_lemma_with_consonant_stem(cls.de_palatalize_stem(stem, 2))
        ) is not None:
            return lemma

        return PresentLemmatizer.modify_stem(stem, tagset)
