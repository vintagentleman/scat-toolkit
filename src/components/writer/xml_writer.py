from pathlib import Path
from typing import List

from lxml import etree

from models.row import Row
from components.xml_processor import XMLProcessor
from .writer import Writer


class XMLWriter(Writer):
    def __init__(self, path: Path):
        super().__init__(path)

        self.stream = etree.XMLParser(remove_blank_text=True)
        self.stream.feed(
            f"""<?xml version="1.0" encoding="UTF-8"?>
            <TEI xmlns="http://www.tei-c.org/ns/1.0">
                <teiHeader>
                    <fileDesc>
                        <titleStmt>
                            <title>{self.manuscript.title}</title>
                        </titleStmt>
                    </fileDesc>
                </teiHeader>
                <text>
                    <body>
                        <ab>
                            <pb n="{self.manuscript.page}{self.manuscript.column}"/>
                            <lb n="{self.manuscript.line}"/>"""
        )

    def write_row(self, row: Row):
        self.stream.feed(f"\n{row.xml()}")

    def write_chunk(self, chunk: List[Row]):
        self.stream.feed(f'<s n="{self.manuscript.chunk_id}">')
        super().write_chunk(chunk)
        self.stream.feed("</s>")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stream.feed(
            """
                        </ab>
                    </body>
                </text>
            </TEI>
            """
        )

        root = self.stream.close()

        with self.path.open(mode="w", encoding="utf-8") as fileobject:
            fileobject.write(
                XMLProcessor(etree.tostring(root, encoding="utf-8"))
                .run()
                .toprettyxml(indent="  ", encoding="utf-8")
                .decode()
            )
