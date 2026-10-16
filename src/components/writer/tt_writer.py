import html
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union

from models.row import Row, WordRow, XMLRow
from models.tagset import Tagset
from models.word import Word

from .writer import Writer

MISSING_VALUE = " "


@dataclass
class _Token:
    values: List[str]
    kind: str = "word"

    def render(self) -> str:
        return "\t".join(self.values)


@dataclass
class _Span:
    name: str
    children: List[_Token] = field(default_factory=list)
    value: int | None = None


@dataclass
class _Tag:
    source: str


@dataclass
class _Boundary:
    """An omitted milestone that still separates neighbouring XML elements."""


_Event = Union[_Token, _Span, _Tag, _Boundary]


class TreeTaggerWriter(Writer):
    """Write SCAT rows directly in the TreeTagger format accepted by Annatto."""

    def __init__(self, path: Path):
        super().__init__(path)
        self.stream = path.open(mode="w", encoding="utf-8")
        self.events: List[_Event] = []
        self.has_morphology = False
        self.has_text_structure = False

    @staticmethod
    def _token(values: List[str], kind: str = "word") -> _Token:
        return _Token([html.unescape(value) for value in values], kind)

    def _word_event(self, word: Word) -> _Event:
        tagset = word.tagset
        is_number = word.is_cardinal_number() or word.is_ordinal_number()

        pos = MISSING_VALUE
        msd = MISSING_VALUE
        if tagset is not None and not word.is_cardinal_number():
            pos = tagset.pos
            if type(tagset) is not Tagset:
                msd = str(tagset)

        token = self._token(
            [
                str(word),
                pos,
                msd,
                word.lemma if word.lemma is not None else MISSING_VALUE,
                word.norm,
                f"{word.manuscript_id}.{word.id}",
            ]
        )

        # An empty erroneous reading can occur in a correction such as
        # ``~ <ПО(Д)ЯВЪ>``. TEI-to-TT omitted the empty token but its ID had
        # already been consumed by the TEI writer.
        if not token.values[0]:
            return _Boundary()

        if word.is_proper:
            return _Span("name", [token])
        if is_number:
            return _Span("num", [token], int(word.norm.split("-", 1)[0]))
        return token

    def _punctuation_events(self, source: str, manuscript_id: str) -> List[_Event]:
        events: List[_Event] = []

        for element in filter(bool, re.split(r"(\[|\])", source)):
            if element == "[":
                events.extend(
                    [
                        _Tag('<add place="margin">'),
                        self._token([element] + [MISSING_VALUE] * 5, "c"),
                    ]
                )
            elif element == "]":
                events.extend(
                    [
                        self._token([element] + [MISSING_VALUE] * 5, "c"),
                        _Tag("</add>"),
                    ]
                )
            else:
                # As in the TEI representation, a punctuation cluster has one ID.
                punctuation = self._token(
                    [element]
                    + [MISSING_VALUE] * 4
                    + [f"{manuscript_id}.{self.manuscript.token_id}"],
                    "pc",
                )
                events.append(punctuation)

        return events

    def write_row(self, row: Row):
        if isinstance(row, XMLRow):
            # Page and line milestones were discarded by tei-to-tt and are not
            # useful as TreeTagger spans. Other source structure is preserved.
            if not re.match(r"^</?(?:lb|pb|milestone)\b", row.source):
                if match := re.fullmatch(r"(<[^>]+>)(.+)", row.source):
                    # Preserve text following a tag as its own TreeTagger line,
                    # as XML pretty-printing did in the former conversion path.
                    self.events.extend([_Tag(match.group(1)), _Tag(match.group(2))])
                else:
                    self.events.append(_Tag(row.source))
                self.has_text_structure = True
            return

        if not isinstance(row, WordRow):
            return

        if row.head_punctuation is not None:
            self.events.extend(
                self._punctuation_events(
                    row.head_punctuation.source,
                    row.head_punctuation.manuscript_id,
                )
            )

        if row.word is not None:
            self.has_morphology |= (
                row.word.tagset is not None and not row.word.is_cardinal_number()
            )
            self.events.append(self._word_event(row.word))
            if row.word.error is not None:
                # The omitted TEI correction note still separated this word
                # from the following element during XML post-processing.
                self.events.append(_Boundary())

        if row.tail_punctuation is not None:
            self.events.extend(
                self._punctuation_events(
                    row.tail_punctuation.source,
                    row.tail_punctuation.manuscript_id,
                )
            )

        # Milestones are omitted from the final file, but they must remain a
        # boundary while names and numeral groups are merged. In the old
        # pipeline they separated nodes in TEI and were removed only later.
        if row.milestone is not None:
            self.events.append(_Boundary())

    @staticmethod
    def _merge_numbers(events: List[_Event]) -> None:
        """Apply the numeral grouping formerly done by XMLProcessor."""

        index = 0
        while index < len(events):
            event = events[index]
            if not isinstance(event, _Span) or event.name != "num":
                index += 1
                continue

            if index > 0:
                previous = events[index - 1]
                if isinstance(previous, _Token) and previous.kind == "pc":
                    event.children.insert(0, previous)
                    del events[index - 1]
                    index -= 1

            while index + 1 < len(events):
                following = events[index + 1]
                if isinstance(following, _Token) and following.kind == "pc":
                    event.children.append(following)
                    del events[index + 1]
                elif isinstance(following, _Span) and following.name == "num":
                    event.children.extend(following.children)
                    event.value = (event.value or 0) + (following.value or 0)
                    del events[index + 1]
                else:
                    break

            index += 1

    @staticmethod
    def _merge_names(events: List[_Event]) -> None:
        """Combine adjacent proper words into a single name span."""

        index = 0
        while index + 1 < len(events):
            current = events[index]
            following = events[index + 1]
            if (
                isinstance(current, _Span)
                and current.name == "name"
                and isinstance(following, _Span)
                and following.name == "name"
            ):
                current.children.extend(following.children)
                del events[index + 1]
            else:
                index += 1

    @staticmethod
    def _render_event(event: _Event) -> List[str]:
        if isinstance(event, _Token):
            return [event.render()]
        if isinstance(event, _Tag):
            return [event.source]
        if isinstance(event, _Boundary):
            return []

        start = f'<num value="{event.value}">' if event.name == "num" else "<name>"
        return [
            start,
            *(child.render() for child in event.children),
            f"</{event.name}>",
        ]

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._merge_numbers(self.events)
        self._merge_names(self.events)

        manuscript_id = self.path.stem
        metadata = {
            "id": manuscript_id,
            "title": self.manuscript.title,
            "century": self.manuscript.century,
            "morphology": str(self.has_morphology).lower(),
            "text_structure": str(self.has_text_structure).lower(),
        }
        attributes = " ".join(
            f'{key}="{html.escape(str(value), quote=True)}"'
            for key, value in metadata.items()
        )

        lines = [f"<doc {attributes}>"]
        for event in self.events:
            lines.extend(self._render_event(event))
        lines.append("</doc>")

        self.stream.write("\n".join(lines))
        self.stream.close()
