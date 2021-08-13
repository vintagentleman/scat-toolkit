from abc import abstractmethod
from contextlib import AbstractContextManager
from pathlib import Path

from lxml import etree

from models.row import Row
from src import manuscripts
from .xml_processor import XMLProcessor
from .unicode_converter import UnicodeConverter


class Writer(AbstractContextManager):
    @abstractmethod
    def __init__(self, path: Path):
        self.path = path
        self.stream = NotImplemented

    @abstractmethod
    def write(self, row: Row):
        pass

    @staticmethod
    def factory(mode: str, path: Path):
        if mode == "txt":
            return TXTWriter(path)
        if mode == "xml":
            return XMLWriter(path)
        raise NotImplementedError()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stream.close()


class TXTWriter(Writer):
    def __init__(self, path: Path):
        super().__init__(path)
        self.stream = Path.open(path, mode="w", encoding="utf-8")

    def write(self, row: Row):
        self.stream.write(UnicodeConverter.convert(str(row)) + " ")


class XMLWriter(Writer):
    def __init__(self, path: Path):
        super().__init__(path)
        self.manuscript = manuscripts[path.stem]

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

    def write(self, row: Row):
        self.stream.feed(f"\n{row.xml()}")

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
