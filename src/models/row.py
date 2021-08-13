import re
from typing import List

from .conll.conll import UPunctuation, UWord
from .milestone import Milestone
from .punctuation import Punctuation
from .word import Word


class Row:
    def __init__(self, manuscript_id: str, columns: List[str]):
        assert len(columns) == 7
        columns = [column.strip() for column in columns]

        source = columns[0]
        self.head_punctuation = None
        self.milestone = None
        self.tail_punctuation = None

        # Extract punctuation from beginning
        if (match := re.search(rf"^{Punctuation.REGEX}+", source)) is not None:
            source, self.head_punctuation = (
                source[match.end() :].strip(),
                Punctuation(manuscript_id, match.group()),
            )

        # Extract break characters from end
        if (match := re.search(rf"{Milestone.REGEX}$", source)) is not None:
            source, self.milestone = (
                source[: match.start()].strip(),
                Milestone.factory(manuscript_id, match.group()),
            )

        # Extract punctuation from end
        if (match := re.search(rf"{Punctuation.REGEX}+$", source)) is not None:
            source, self.tail_punctuation = (
                source[: match.start()].strip(),
                Punctuation(manuscript_id, match.group()),
            )

        self.word = Word(manuscript_id, source, columns[1:]) if source else None

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
