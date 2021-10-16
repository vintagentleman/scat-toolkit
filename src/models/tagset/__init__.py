import re
from typing import List

from utils import replace_chars
from utils.characters import cyrillic_lowercase_homoglyphs, latin_lowercase_homoglyphs

from .noun_tagset import NounTagset
from .participle_tagset import ParticipleTagset
from .pronoun_tagset import PronounTagset
from .tagset import Tagset
from .verb_tagset import VerbTagset


def tagset_factory(columns: List[str]):
    pos = replace_chars(
        columns[0], latin_lowercase_homoglyphs, cyrillic_lowercase_homoglyphs
    )

    # Ignore ambiguous part of speech
    if "/" in pos and not re.search(r"/([внп]|ср)$", pos):
        pos = pos.split("/")[-1]

    if pos in ("сущ", "прил", "прил/ср", "числ", "числ/п"):
        return NounTagset(pos, columns[1:])
    if pos == "мест":
        return (
            PronounTagset(pos, columns[1:])
            if columns[1] == "личн"
            else NounTagset(pos, columns[1:])
        )
    if pos in ("гл", "гл/в"):
        return VerbTagset(pos, columns[1:])
    if pos in ("прич", "прич/в"):
        return ParticipleTagset(pos, columns[1:])

    return Tagset(pos)
