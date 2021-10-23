import re
from typing import Optional

from models.word import Word
from utils import characters

from .lib import infl, specials, verbs
from .verb_lemmatizer import VerbLemmatizer


class ParticipleLemmatizer(VerbLemmatizer):
    @classmethod
    def lemmatize(cls, word: Word) -> Optional[str]:
        norm = word.norm
        tagset = word.tagset
        suffix = None

        if tagset.is_reflexive:
            norm = norm[:-2]
        if re.match("НЕ(?!(ДО|НАВИ))", norm):
            norm = norm[2:]
        if not norm.endswith(characters.vowels):
            norm = f"{norm}`"

        if tagset.declension[0] in ("тв", "м"):
            stem = cls.get_stem(
                norm,
                (tagset.declension[1], tagset.case, tagset.number, tagset.gender),
                infl.pronoun,
            )

            if stem is None and tagset.declension[0] == "м":
                stem = cls.get_stem(
                    norm,
                    ("тв", tagset.case, tagset.number, tagset.gender),
                    infl.pronoun,
                )
        elif (tagset.voice, tagset.case, tagset.number, tagset.gender) not in (
            ("акт", "им", "ед", "м"),
            ("акт", "им", "ед", "ср"),
        ):
            stem = cls.get_stem(
                norm,
                (tagset.declension[1], tagset.case, tagset.number, tagset.gender),
                infl.noun,
            )

            if stem is None and tagset.declension[0] == "ja":
                stem = cls.get_stem(
                    norm, ("jo", tagset.case, tagset.number, tagset.gender), infl.noun,
                )
        else:
            stem = norm[:-1]
            suffix = norm[-1]

        if stem is None:
            return None

        if tagset.tense == "наст":
            if suffix is None:
                if tagset.voice == "акт":
                    if (mo := re.search(r".Щ$", stem)) is None:
                        mo = re.search(r"[АЫЯ]$", stem)
                else:
                    mo = re.search(r".М$", stem)

                if mo is not None:
                    suffix = mo.group()
                    stem = stem[: -len(suffix)]

            # 5 класс
            lemma = cls.cls_5(stem)

            if lemma is None:
                # Основы на согласный
                lemma = cls.get_lemma_with_consonant_stem(stem)

                if lemma is None:
                    lemma = (
                        ActivePresentLemmatizer
                        if tagset.voice == "акт"
                        else PassivePresentLemmatizer
                    ).modify_stem(stem, suffix)
            else:
                lemma = (
                    ActivePastLemmatizer
                    if tagset.voice == "акт"
                    else PassivePastLemmatizer
                ).modify_stem(stem)

        else:
            lemma = (
                ActivePastLemmatizer if tagset.voice == "акт" else PassivePastLemmatizer
            ).modify_stem(stem)

        if lemma is not None and tagset.is_reflexive:
            return f"{lemma}СЯ"
        return lemma


class ActivePresentLemmatizer(ParticipleLemmatizer):
    @classmethod
    def modify_stem(cls, stem: str, suffix: str) -> Optional[str]:
        if cls.is_stem_in_dictionary(stem, verbs.cls_vii_2):
            return cls.cls_1(stem)
        if suffix in ("Ы", "УЩ"):
            return cls.cls_2(stem) if stem.endswith("Н") else cls.cls_1(stem)
        if suffix == "ЮЩ" or (
            suffix == "УЩ"
            and stem.endswith(
                characters.hush_consonants + characters.sonorant_consonants
            )
        ):
            return cls.cls_3(stem)
        if suffix in ("АЩ", "ЯЩ", "ИЩ"):
            return cls.cls_4(stem)
        if stem.endswith(("А", "+")):
            return cls.cls_3(stem)

        if stem.endswith(characters.hush_consonants) or stem.endswith(
            characters.sonorant_consonants
        ):
            stem = cls.modify_jot(stem)

        if cls.is_stem_in_dictionary(stem, verbs.cls_x_e):
            return stem + "+ТИ"
        if cls.is_stem_in_dictionary(stem, verbs.cls_x_a):
            return (
                stem
                + ("А" if stem.endswith(characters.hush_consonants) else "Я")
                + "ТИ"
            )
        if cls.is_stem_in_dictionary(stem, verbs.cls_x_i):
            return stem + "ИТИ"

        return cls.cls_3(stem) if suffix in ("А", "Я") else None


class PassivePresentLemmatizer(ParticipleLemmatizer):
    @classmethod
    def modify_stem(cls, stem: str, suffix: str) -> Optional[str]:
        if suffix == "ОМ":
            return cls.cls_1(stem)
        if suffix == "ЕМ":
            return cls.cls_3(stem)
        if suffix == "ИМ":
            return cls.cls_4(stem)
        return None


class ActivePastLemmatizer(ParticipleLemmatizer):
    @classmethod
    def modify_stem(cls, stem: str) -> Optional[str]:
        # Удаление словоизменительных суффиксов
        if (suffix := re.search("В$|В?[ЕЪЬ]?Ш$", stem)) is not None:
            stem = stem[: -len(suffix.group())]

        # Основы-исключения
        if (modified_stem := cls.get_special_verb_stem(stem, specials.part)) != stem:
            return modified_stem + "ТИ"

        # Основы на согласный
        if (lemma := cls.get_lemma_with_consonant_stem(stem)) is not None:
            return lemma

        # Сочетания с йотом
        if stem.endswith(characters.hush_consonants + characters.sonorant_consonants):
            stem = cls.modify_jot(stem) + "И"
        # 4 класс
        elif stem[-1] in characters.consonants or stem in verbs.cls_iv_vow:
            stem += "НУ"

        return stem + "ТИ"


class PassivePastLemmatizer(ParticipleLemmatizer):
    @classmethod
    def modify_stem(cls, stem: str) -> Optional[str]:
        # Удаление словоизменительных суффиксов
        if (suffix := re.search("Е?Н?Н$|Т$", stem)) is not None:
            stem = stem[: -len(suffix.group())]

        # Основы на согласный
        if (
            lemma := cls.get_lemma_with_consonant_stem(cls.de_palatalize_stem(stem, 1))
        ) is not None:
            return lemma

        # Сочетания с йотом
        if stem.endswith(characters.hush_consonants + characters.sonorant_consonants):
            stem = cls.modify_jot(stem) + "И"

        # Чередование /u:/
        elif suffix and suffix.group().startswith("ЕН"):
            stem = cls.modify_uu(stem) if stem[-1] == "В" else stem + "И"

        # 4 класс
        elif stem[-1] in characters.consonants or cls.is_stem_in_dictionary(
            stem, verbs.cls_iv_vow
        ):
            stem += "НУ"

        return stem + "ТИ"
