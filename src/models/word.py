import re
from typing import List, Optional

from components.unicode_converter import UnicodeConverter
from models.milestone import Milestone
from models.tagset import Tagset
from utils.characters import latin_homoglyphs, cyrillic_homoglyphs
from utils import replace_chars


class Word:
    def __init__(self, manuscript_id: str, source: str, grammemes: List[str]):
        self.manuscript_id = manuscript_id
        self.source = replace_chars(source, latin_homoglyphs, cyrillic_homoglyphs)
        self.correction = None

        # Extract correction with break characters removed
        if "<" in source:
            self.source, self.correction = (
                self.source[: self.source.index("<") - 1],
                self.source[self.source.index("<") + 1 : self.source.index(">")],
            )

        # Check that tagset is not empty before assignment
        self.tagset = Tagset.factory(grammemes) if grammemes[0] else None

        self.norm: Optional[str] = None
        self.lemma: Optional[str] = None

    def is_cardinal_number(self) -> bool:
        return self.tagset is not None and self.tagset.pos.isnumeric()

    def is_ordinal_number(self) -> bool:
        return (
            "#" in self.source
            and self.tagset is not None
            and self.tagset.pos == "числ/п"
        )

    def is_proper(self) -> bool:
        return "*" in self.source

    @property
    def orig(self) -> str:
        # Remove erroneous spelling and proper name markers
        source = self.source[1:] if self.source.startswith(("*", "~")) else self.source

        # Split word by milestones. Final condition filters out empty strings.
        # Note that converting milestones to XML mutates global manuscript objects.
        elements: List[str] = [
            Milestone.factory(self.manuscript_id, element).xml
            if element.startswith(("&", "\\", "Z"))
            else element
            for element in re.split(Milestone.REGEX, source)
            if element
        ]

        return UnicodeConverter.convert("".join(elements))

    def __str__(self):
        return re.sub(
            Milestone.REGEX,
            "",
            self.correction if self.correction is not None else self.source,
        )

    @property
    def xml(self) -> str:
        attrs = []

        if not self.is_cardinal_number():
            attrs.append(f'pos="{self.tagset.pos}"')
            if (
                type(self.tagset) != Tagset
            ):  # Only members of strict subclasses have annotation
                attrs.append(f'msd="{str(self.tagset)}"')

        if self.norm is not None:
            attrs.append(f'norm="{self.norm}"')
        if self.lemma is not None:
            attrs.append(f'lemma="{self.lemma}"')

        res = f"<w {' '.join(attrs)}>{self.orig}</w>"

        if self.is_proper():
            res = f"<name>{res}</name>"
        elif self.is_cardinal_number() or self.is_ordinal_number():
            res = f"<num>{res}</num>"

        if self.correction is not None:
            res += f'<note type="corr">{UnicodeConverter.convert(str(self))}</note>'

        return res
