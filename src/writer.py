from abc import abstractmethod
from contextlib import AbstractContextManager
from pathlib import Path
import shelve

from lxml import etree

from src import __metadata__
from models import Word


class Writer(AbstractContextManager):
    @abstractmethod
    def __init__(self, path):
        self.path = path
        self.stream = NotImplemented

    @abstractmethod
    def write(self, *args):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stream.close()


class TSVWriter(Writer):
    def __init__(self, path):
        super().__init__(path)
        self.stream = Path.open(path, mode="w", encoding="utf-8")

    def write(self, *args):
        self.stream.write("\t".join([str(arg) for arg in args]) + "\n")


class PKLWriter(Writer):
    def __init__(self, path):
        super().__init__(path)
        self.stream = shelve.open(str(path), writeback=True)

    def write(self, *args):
        msd = self.stream.setdefault(args[0], [])

        if args[1] not in msd:
            msd.append(args[1])


class XMLWriter(Writer):
    def __init__(self, path):
        super().__init__(path)
        self.stream = etree.XMLParser(remove_blank_text=True)

        self.idx = 0
        self.meta = __metadata__[path.stem]

        self.stream.feed(
            f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>{self.meta["title"]}</title>
      </titleStmt>
    </fileDesc>
  </teiHeader>
  <text>
    <body>
      <ab>
        <pb n="{self.meta["page"] + self.meta["column"]}"/>
        <lb n="1"/>"""
        )

    def write(self, *args):
        row, res = args[0], []

        if row.pcl:  # Пунктуация слева
            punct = row.pcl.replace("[", "")
            token = row.pcl.replace("[", '<add place="margin"><c>[</c>')
            if punct:
                force = "strong" if punct in (":", ";") else "weak"
                token = token.replace(
                    punct,
                    f'<pc xml:id="{self.path.stem}.{self.idx}" force="{force}">{punct}</pc>',
                )
                self.idx += 1
            res.append(token)

        if row.word:  # Словоформа
            res.append(str(Word(self.path.stem, self.idx, row.word, row.ana)))
            self.idx += 1

        if row.pcr:  # Пунктуация справа
            punct = row.pcr.replace("]", "")
            token = row.pcr.replace("]", "<c>]</c></add>")
            if punct:
                force = "strong" if punct in (":", ";") else "weak"
                token = token.replace(
                    punct,
                    f'<pc xml:id="{self.path.stem}.{self.idx}" force="{force}">{punct}</pc>',
                )
                self.idx += 1
            res.append(token)

        if row.br is not None:  # Висячие разрывы
            if "&" in row.br.group():
                self.meta["line"] += 1
                res.append(f'<lb n="{self.meta["line"]}"/>')
            elif "\\" in row.br.group() or "Z" in row.br.group():
                if "\\" in row.br.group():
                    self.meta["column"] = "b"
                else:
                    self.meta["page"], self.meta["column"] = (
                        row.br.group(1),
                        "a" if self.meta["column"] else "",
                    )

                self.meta["line"] += 1
                res.append(
                    f'<pb n="{self.meta["page"] + self.meta["column"]}"/><lb n="1"/>'
                )

        self.stream.feed("\n".join(res) + "\n")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stream.feed("</ab></body></text></TEI>")

        root = self.stream.close()
        etree.ElementTree(root).write(
            str(self.path), encoding="utf-8", xml_declaration=True, pretty_print=True
        )
