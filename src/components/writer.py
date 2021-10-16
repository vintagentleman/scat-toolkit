import shelve
from abc import abstractmethod
from contextlib import AbstractContextManager
from pathlib import Path
from typing import List

from lxml import etree

from models.row import Row
from src import manuscripts

from .pickler import Pickler
from .xml_processor import XMLProcessor


class Writer(AbstractContextManager):
    @abstractmethod
    def __init__(self, path: Path):
        self.path = path
        self.manuscript = manuscripts[path.stem]
        self.stream = NotImplemented

    @abstractmethod
    def write_row(self, row: Row):
        pass

    def write_chunk(self, chunk: List[Row]):
        [self.write_row(row) for row in chunk]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stream.close()


class TXTWriter(Writer):
    def __init__(self, path: Path):
        super().__init__(path)
        self.stream = Path.open(path, mode="w", encoding="utf-8")

    def write_row(self, row: Row):
        self.stream.write(str(row) + " ")

    def write_chunk(self, chunk: List[Row]):
        super().write_chunk(chunk)
        self.stream.write("\n")


class TSVWriter(TXTWriter):
    def __init__(self, path):
        super().__init__(path)
        self.stream = Path.open(path, mode="w", encoding="utf-8")

    def write_row(self, row: Row):
        self.stream.write(
            f"{row.tsv()}\t{row.word.lemma if row.word is not None else ''}\n"
        )


class PKLWriter(Writer):
    def __init__(self, path):
        super().__init__(path)
        self.stream = shelve.open(str(path), writeback=True)

    def write_row(self, row: Row):
        if row.word is None or row.word.tagset is None:
            return

        options = self.stream.setdefault(row.word.norm, [])

        if (pickled := Pickler.pickle(row.word)) not in options:
            options.append(pickled)


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


class CoNLLWriter(Writer):
    def __init__(self, path: Path):
        super().__init__(path)
        self.stream = Path.open(path, mode="w", encoding="utf-8")

    def write_row(self, row: Row):
        if text := row.conll():
            self.stream.write(text + "\n")

    def write_chunk(self, chunk: List[Row]):
        self.stream.write(f"# source = {self.manuscript.title}\n")
        self.stream.write(f"# text = {' '.join([str(row) for row in chunk])}\n")
        self.stream.write(f"# sent_id = {self.manuscript.chunk_id}\n")

        super().write_chunk(chunk)

        self.stream.write("\n")
        self.manuscript.token_id = 0


def writer_factory(mode: str, path: Path) -> Writer:
    if mode == "txt":
        return TXTWriter(path)
    if mode == "tsv":
        return TSVWriter(path)
    if mode == "pkl":
        return PKLWriter(path)
    if mode == "xml":
        return XMLWriter(path)
    if mode == "conll":
        return CoNLLWriter(path)
    raise NotImplementedError
