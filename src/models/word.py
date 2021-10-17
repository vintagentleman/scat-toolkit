import re
from typing import List, Optional

from components.unicode_converter import UnicodeConverter
from models.milestone import milestone_factory, Milestone
from models.tagset import Tagset, tagset_factory
from src import manuscripts
from utils import replace_chars
from utils.characters import cyrillic_homoglyphs, latin_homoglyphs


class Word:
    def __init__(self, manuscript_id: str, source: str, grammemes: List[str]):
        self.manuscript_id = manuscript_id
        self.source = replace_chars(source, latin_homoglyphs, cyrillic_homoglyphs)
        self.error = None

        # Extract correction with break characters removed
        if "<" in source:
            self.error, self.source = (
                self.source[1 : self.source.index("<") - 1],  # Text between ~ and <
                self.source[
                    self.source.index("<") + 1 : self.source.index(">")
                ],  # Text between < and >
            )

        self.is_proper = self.source.startswith("*")
        self.source = (
            self.source[1:] if self.is_proper else self.source
        )  # Remove property marker

        # Check that tagset is not empty before assignment
        self.tagset = tagset_factory(grammemes) if grammemes[0] else None

        self.pos = (
            self.tagset.pos if self.tagset is not None else None
        )  # Add POS alias for convenience
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

    def source_without_milestones(self) -> str:
        return re.sub(Milestone.REGEX, "", self.source)

    def source_to_unicode(self) -> str:
        return UnicodeConverter.convert(self.source_without_milestones())

    @property
    def id(self):
        return manuscripts[self.manuscript_id].token_id

    @property
    def orig(self) -> str:
        orig = self.source if self.error is None else self.error

        # Split word by milestones. Final condition filters out empty strings.
        # Note that converting milestones to XML mutates global manuscript objects.
        elements: List[str] = [
            milestone_factory(self.manuscript_id, element).xml()
            if element.startswith(("&", "\\", "Z"))
            else element
            for element in re.split(Milestone.REGEX, orig)
            if element
        ]

        return UnicodeConverter.convert("".join(elements))

    def __str__(self):
        return UnicodeConverter.convert(
            re.sub(
                Milestone.REGEX, "", self.source if self.error is None else self.error
            )
        )

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
            attrs.append(f'lemma="{self.lemma.replace("+", "Ѣ").lower()}"')

        res = f'<w xml:id="{self.manuscript_id}.{self.id}" {" ".join(attrs)}>{self.orig}</w>'

        if self.is_proper:
            res = f"<name>{res}</name>"
        elif self.is_cardinal_number() or self.is_ordinal_number():
            res = f"<num>{res}</num>"

        if self.error is not None:
            res += f'<note type="corr">{self.source_to_unicode()}</note>'

        return res
