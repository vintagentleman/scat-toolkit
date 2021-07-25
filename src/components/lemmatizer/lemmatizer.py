import re
from typing import Optional

from models.word import Word
from utils import characters


class Lemmatizer:
    @classmethod
    def lemmatize(cls, word: Word) -> Optional[str]:
        lemma = word.norm

        if lemma.endswith(characters.consonants):
            lemma += "Ь" if lemma[-1] in characters.hush_consonants else "Ъ"

        return lemma

    @staticmethod
    def get_stem(norm: str, grammemes: tuple, infl_dict: dict) -> Optional[str]:
        if grammemes not in infl_dict:
            return None

        suffix = re.search("({}|`)$".format(infl_dict[grammemes]), norm)
        return norm[: -len(suffix.group())] if suffix else None
