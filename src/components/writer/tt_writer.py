import html
import re
from pathlib import Path
from typing import Iterator
from xml.dom.minidom import Element, Text

from models.row import Row, XMLRow

from .xml_writer import XMLWriter

MISSING_VALUE = " "
OMITTED = ("lb", "pb", "milestone", "note")


def _text(node) -> str:
    return "".join(
        child.data if isinstance(child, Text) else _text(child)
        for child in node.childNodes
    )


def _lines(parent: Element) -> Iterator[str]:
    for node in parent.childNodes:
        if isinstance(node, Text):
            yield node.data
        elif not isinstance(node, Element) or node.tagName in OMITTED:
            continue
        elif node.tagName == "w":
            # An editor-inserted word (`~ <…>`) has an empty reading and is left out
            if token := _text(node):
                yield "\t".join(
                    [
                        token,
                        *(
                            node.getAttribute(a) or MISSING_VALUE
                            for a in ("pos", "msd", "lemma")
                        ),
                        node.getAttribute("norm"),
                        node.getAttribute("xml:id"),
                    ]
                )
        elif node.tagName in ("pc", "c"):
            yield "\t".join(
                [
                    _text(node),
                    *[MISSING_VALUE] * 4,
                    node.getAttribute("xml:id") or MISSING_VALUE,
                ]
            )
        else:
            attributes = "".join(
                f' {name}="{html.escape(value)}"'
                for name, value in node.attributes.items()
            )
            yield f"<{node.tagName}{attributes}>"
            yield from _lines(node)
            yield f"</{node.tagName}>"


class TreeTaggerWriter(XMLWriter):
    """Write the processed TEI document in the TreeTagger format accepted by Annatto."""

    def __init__(self, path: Path):
        super().__init__(path)
        self.has_text_structure = False

    def write_row(self, row: Row):
        if isinstance(row, XMLRow) and not re.match(
            r"^</?(?:lb|pb|milestone)\b", row.source
        ):
            self.has_text_structure = True
        super().write_row(row)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            return

        document = self.document()
        has_morphology = any(
            w.hasAttribute("pos") for w in document.getElementsByTagName("w")
        )
        metadata = {
            "id": self.path.stem,
            "title": self.manuscript.title,
            "century": self.manuscript.century,
            "morphology": str(has_morphology).lower(),
            "text_structure": str(self.has_text_structure).lower(),
        }
        attributes = " ".join(
            f'{key}="{html.escape(str(value))}"' for key, value in metadata.items()
        )
        lines = [
            f"<doc {attributes}>",
            *_lines(document.getElementsByTagName("ab")[0]),
            "</doc>",
        ]

        with self.path.open(mode="w", encoding="utf-8") as fileobject:
            fileobject.write("\n".join(lines) + "\n")
