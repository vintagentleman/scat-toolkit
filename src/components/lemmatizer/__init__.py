from models.tagset import PronounTagset
from models.word import Word

from .adjective_lemmatizer import AdjectiveLemmatizer
from .lemmatizer import Lemmatizer
from .noun_lemmatizer import NounLemmatizer
from .numeral_lemmatizer import NumeralLemmatizer
from .participle_lemmatizer import ParticipleLemmatizer
from .pronoun_lemmatizer import PronounLemmatizer
from .supine_lemmatizer import SupineLemmatizer
from .verb_lemmatizer import VerbLemmatizer


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
            if type(word.tagset) is PronounTagset
            else NumeralLemmatizer
        )
    if word.pos in ("гл", "гл/в"):
        return VerbLemmatizer
    if word.pos in ("прич", "прич/в"):
        return ParticipleLemmatizer
    if word.pos == "суп":
        return SupineLemmatizer
    return Lemmatizer
