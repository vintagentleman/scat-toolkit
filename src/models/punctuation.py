import re
from typing import List

from src import manuscripts


class Punctuation:
    REGEX = r"[.,:;[\]]"

    def __init__(self, manuscript_id: str, source: str):
        self.manuscript_id = manuscript_id
        self.source = source

    @property
    def id(self):
        return manuscripts[self.manuscript_id].token_id

    def xml(self) -> str:
        # Split possible multiple punctuation and filter out empty elements
        elements: List[str] = [
            element for element in re.split(r"(\[|\])", self.source) if element
        ]

        for i, element in enumerate(elements):
            if element == "[":
                elements[i] = '<add place="margin"><c>[</c>'
            elif element == "]":
                elements[i] = "<c>]</c></add>"
            else:
                elements[
                    i
                ] = f'<pc xml:id="{self.manuscript_id}.{self.id}">{element}</pc>'

        return "".join(elements)
