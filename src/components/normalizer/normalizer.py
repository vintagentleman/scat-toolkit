from utils import characters, replace_chars

from components.normalizer.modif import modif
from models.number import Number
from models.word import Word


class Normalizer:
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
        res = str(word).strip().upper()

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
