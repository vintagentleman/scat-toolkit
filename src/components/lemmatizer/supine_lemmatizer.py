from typing import Optional

from models.word import Word

from .lemmatizer import Lemmatizer


class SupineLemmatizer(Lemmatizer):
    def lemmatize(self, word: Word) -> Optional[str]:
        return word.norm[:-1] + "И"
