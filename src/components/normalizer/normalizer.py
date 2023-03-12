import re

from components.normalizer.modif import modif
from models.milestone import Milestone
from models.number import Number
from models.word import Word
from utils import characters, replace_chars


class Normalizer:
    @staticmethod
    def _replace_yer_before_linebreak(source: str) -> str:
        for cluster in ("Ъ&", "ЪZ", "Ь&", "ЬZ"):
            if cluster in source and not (
                source.endswith(cluster)  # Yer shouldn't be in word-final position
                or source[1:].startswith(
                    cluster
                )  # Yer shouldn't be part of a prefix e.g. ВЪ-, СЪ-
                or source[source.index(cluster) - 1] == "Л"  # Yer shouldn't follow -Л-
            ):
                return source.replace(cluster, "")
        return source

    @staticmethod
    def _replace_izhitsa(source: str, idx: int) -> str:
        try:
            prev_char, next_char = source[idx - 1], source[idx + 1]
        except IndexError:
            return "И"

        if (
            prev_char == "Е"
            or prev_char in characters.vowels
            and next_char in characters.vowels + characters.sonorant_consonants
        ):
            return "В"

        return "И"

    @classmethod
    def normalize(cls, word: Word) -> str:
        res = word.source.strip().upper()

        # Remove yer before linebreak unless tagged otherwise
        if word.tagset is not None and word.tagset.note is not None and not (
            "+ъ" in word.tagset.note or "+ь" in word.tagset.note
        ):
            res = cls._replace_yer_before_linebreak(res)

        # Remove milestones
        res = re.sub(Milestone.REGEX, "", res)

        if word.is_cardinal_number():
            return word.tagset.pos  # Non-spelled out numerals
        if word.is_ordinal_number():
            return str(
                Number(res.replace("(", "").replace(")", "").replace(" ", ""))
            )  # Spelled-out numerals

        res = replace_chars(
            res,
            characters.latin_special_characters,
            characters.cyrillic_special_characters,
        )

        for idx in [
            idx for idx, char in enumerate(res) if char == "V"
        ]:  # Izhitsa positional replacement
            res = res[:idx] + cls._replace_izhitsa(res, idx) + res[idx + 1 :]

        # Orthography normalization
        res = modif(res, word.tagset.pos if word.tagset is not None else "")

        return res.replace("#", "").replace("(", "").replace(")", "")
