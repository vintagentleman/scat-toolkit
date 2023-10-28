import datetime
from pathlib import Path
from typing import List

from lxml import etree

from models.row import Row
from models.proiel.proiel import PToken
from data.manuscripts import manuscripts
from .writer import Writer


class ProielXMLWriter(Writer):
    def __init__(self, path):
        super().__init__(path)
        manuscript_id = path.stem.replace(".proiel", "")
        self.manuscript = manuscripts.get(
            manuscript_id
        )  # Filename w/o ".proiel" suffix

        # Root element setup
        self.root = etree.Element("proiel")
        self.root.set(
            "export-time",
            datetime.datetime.utcnow()
            .replace(tzinfo=datetime.timezone.utc)
            .isoformat(),
        )
        self.root.set("schema-version", "2.0")

        self.root.append(
            etree.XML(
                Path.joinpath(Path(__file__).resolve().parents[3], "resources", "proiel_schema.xml")
                .open(encoding="utf-8")
                .read(),
                etree.XMLParser(remove_blank_text=True),
            )
        )

        source = etree.SubElement(self.root, "source")
        source.set("id", manuscript_id)
        source.set("language", "chu")
        etree.SubElement(source, "title").text = self.manuscript.title
        etree.SubElement(source, "citation-part").text = self.manuscript.title

        self.div = etree.SubElement(source, "div")
        etree.SubElement(self.div, "title").text = manuscript_id
        self.sentence = self._new_sentence()

    def _new_sentence(self):
        sentence = etree.SubElement(self.div, "sentence")
        sentence.set("id", str(self.manuscript.chunk_id))
        sentence.set("status", "unannotated")
        return sentence

    def write_chunk(self, chunk: List[Row]):
        super().write_chunk(chunk)
        self.sentence = self._new_sentence()

    def write_row(self, row: Row):
        if row.word is None:
            return

        token = PToken(row).xml()
        token.set("id", str(self.manuscript.token_id))
        self.sentence.append(token)

    def __exit__(self, exc_type, exc_val, exc_tb):
        etree.ElementTree(self.root).write(
            str(self.path), encoding="utf-8", xml_declaration=True, pretty_print=True
        )
