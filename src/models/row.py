import re
from abc import ABC, abstractmethod
from typing import List, Optional

from .conll.conll import UPunctuation, UWord
from .milestone import milestone_factory, Milestone
from .punctuation import Punctuation
from .word import Word


class Row(ABC):
    def __init__(self, manuscript_id: str, columns: List[str]):
        assert len(columns) == 7

        self.columns: List[str] = columns
        self.source: str = self.columns[0]
        self.word: Optional[Word] = None
        self.head_punctuation: Optional[Punctuation] = None
        self.milestone: Optional[Milestone] = None
        self.tail_punctuation: Optional[Punctuation] = None

    def tsv(self) -> str:
        return "\t".join(self.columns)

    @abstractmethod
    def xml(self) -> str:
        pass

    @abstractmethod
    def conll(self) -> str:
        pass


class WordRow(Row):
    def __init__(self, manuscript_id: str, columns: List[str]):
        columns = [column.strip() for column in columns]
        super().__init__(manuscript_id, columns)

        # Extract punctuation from beginning
        if (match := re.search(rf"^{Punctuation.REGEX}+", self.source)) is not None:
            self.source, self.head_punctuation = (
                self.source[match.end() :].strip(),
                Punctuation(manuscript_id, match.group()),
            )

        # Extract break characters from end
        if (match := re.search(rf"{Milestone.REGEX}$", self.source)) is not None:
            self.source, self.milestone = (
                self.source[: match.start()].strip(),
                milestone_factory(manuscript_id, match.group()),
            )

        # Extract punctuation from end
        if (match := re.search(rf"{Punctuation.REGEX}+$", self.source)) is not None:
            self.source, self.tail_punctuation = (
                self.source[: match.start()].strip(),
                Punctuation(manuscript_id, match.group()),
            )

        self.word = (
            Word(manuscript_id, self.source, self.columns[1:]) if self.source else None
        )

    def __str__(self):
        # fmt: off
        return "".join(
            [
                self.head_punctuation.source if self.head_punctuation is not None else "",
                str(self.word) if self.word is not None else "",
                self.tail_punctuation.source if self.tail_punctuation is not None else "",
            ]
        )
        # fmt: on

    def xml(self) -> str:
        # fmt: off
        return "".join(
            [
                self.head_punctuation.xml() if self.head_punctuation is not None else "",
                self.word.xml() if self.word is not None else "",
                self.tail_punctuation.xml() if self.tail_punctuation is not None else "",
                self.milestone.xml() if self.milestone is not None else "",
            ]
        )
        # fmt: on

    def conll(self) -> str:
        # fmt: off
        return "\n".join([row for row in [
                str(UPunctuation(self.head_punctuation)) if self.head_punctuation is not None else "",
                str(UWord(self.word)) if self.word is not None else "",
                str(UPunctuation(self.tail_punctuation)) if self.tail_punctuation is not None else "",
            ] if row
        ])
        # fmt: on


class XMLRow(Row):
    def xml(self) -> str:
        return self.source

    def conll(self) -> str:
        raise NotImplementedError
