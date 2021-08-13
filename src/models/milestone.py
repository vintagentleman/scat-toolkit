import re

from models.manuscript import Manuscript
from src import manuscripts


class Milestone:
    REGEX = r"(@|&|\\|Z\s+-?\d+\s*)"

    def __init__(self, manuscript_id: str):
        self.manuscript: Manuscript = manuscripts[manuscript_id]

    def xml(self) -> str:
        return "<milestone/>"

    @staticmethod
    def factory(manuscript_id: str, source: str):
        if source == "@":
            return Milestone(manuscript_id)
        if source == "&":
            return LineBeginning(manuscript_id)
        if source == "\\":
            return ColumnBeginning(manuscript_id)
        if source.startswith("Z"):
            return PageBeginning(
                manuscript_id, int(re.search(r"-?\d+", source).group())
            )

        raise ValueError(f"Unknown milestone element: {source}")


class LineBeginning(Milestone):
    def xml(self) -> str:
        self.manuscript.line += 1

        return f'<lb n="{self.manuscript.line}"/>'


class ColumnBeginning(Milestone):
    def xml(self) -> str:
        self.manuscript.column = "b"
        self.manuscript.line = 1

        return f'<pb n="{self.manuscript.page}{self.manuscript.column}"/><lb n="{self.manuscript.line}"/>'


class PageBeginning(Milestone):
    def __init__(self, manuscript_id: str, number: int):
        super().__init__(manuscript_id)
        self.number = number

    def xml(self) -> str:
        self.manuscript.page = self.number
        self.manuscript.column = "a" if self.manuscript.column else ""
        self.manuscript.line = 1

        return f'<pb n="{self.manuscript.page}{self.manuscript.column}"/><lb n="{self.manuscript.line}"/>'
