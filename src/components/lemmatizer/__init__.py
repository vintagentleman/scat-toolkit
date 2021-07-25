from models.tagset import PronounTagset
from models.word import Word

from .lemmatizer import Lemmatizer
from .noun_lemmatizer import NounLemmatizer
from .adjective_lemmatizer import AdjectiveLemmatizer
from .numeral_lemmatizer import NumeralLemmatizer
from .pronoun_lemmatizer import PronounLemmatizer
from .verb_lemmatizer import VerbLemmatizer
from .participle_lemmatizer import ParticipleLemmatizer
from .supine_lemmatizer import SupineLemmatizer


def lemmatizer_factory(word: Word):
    if word.pos == "сущ":
        return NounLemmatizer
    if word.pos in ("прил", "прил/ср", "числ/п"):
        return AdjectiveLemmatizer
    if word.pos == "числ":
        return NumeralLemmatizer
    if word.pos == "мест":
        return (
            PronounLemmatizer
            if type(word.tagset) == PronounTagset
            else NumeralLemmatizer
        )
    if word.pos in ("гл", "гл/в"):
        return VerbLemmatizer
    if word.pos in ("прич", "прич/в"):
        return ParticipleLemmatizer
    if word.pos == "суп":
        return SupineLemmatizer
    return Lemmatizer
