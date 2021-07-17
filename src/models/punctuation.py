import re
from typing import List


class Punctuation:
    REGEX = r"[.,:;[\]]"

    def __init__(self, source: str):
        self.source = source

    @property
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
                elements[i] = f"<pc>{element}</pc>"

        return "".join(elements)
