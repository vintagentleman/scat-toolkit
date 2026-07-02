from models.word import ParsedWord

from .lemmatizer import Lemmatizer


class SupineLemmatizer(Lemmatizer):
    @classmethod
    def lemmatize(cls, word: ParsedWord, norm: str) -> str:
        return norm[:-1] + "И"
