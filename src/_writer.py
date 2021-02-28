from abc import abstractmethod
from contextlib import AbstractContextManager
import datetime
from pathlib import Path
import shelve

from lxml import etree

from src import __metadata__, __root__
from _models import Word, ProielWord
from xml_modif import PostProc


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

        with open(str(self.path), mode="w", encoding="utf-8") as fo:
            fo.write(
                PostProc(etree.tostring(root, encoding="utf-8"))
                .run()
                .toprettyxml(indent="  ", encoding="utf-8")
                .decode()
            )


class ProielXMLWriter(Writer):
    def __init__(self, path):
        super().__init__(path)
        self.stream = Path.open(path, mode="w", encoding="utf-8")
        self.text_id = path.stem.replace(".proiel", "")  # Filename w/o ".proiel" suffix
        self.sentence_id = 1  # Sentence ID counter
        self.token_id = 1  # Token ID counter

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
                Path.joinpath(__root__, "conf", "annotation.xml")
                .open(encoding="utf-8")
                .read(),
                etree.XMLParser(remove_blank_text=True),
            )
        )

        # Source metadata setup
        meta = __metadata__[self.text_id]

        source = etree.SubElement(self.root, "source")
        source.set("id", self.text_id)
        source.set("language", "chu")
        etree.SubElement(source, "title").text = meta["title"]
        etree.SubElement(source, "citation-part").text = meta["title"]

        self.div = etree.SubElement(source, "div")
        etree.SubElement(self.div, "title").text = self.text_id
        self.sentence = self._new_sentence()

    def _new_sentence(self):
        sentence = etree.SubElement(self.div, "sentence")
        sentence.set("id", str(self.sentence_id))
        sentence.set("status", "unannotated")
        self.sentence_id += 1
        return sentence

    def write(self, *args):
        row = args[0]

        if not row.word:
            print(f"No word in {self.text_id}, row {row}")
            return

        word = ProielWord(self.text_id, self.token_id, row.word, row.ana)
        token = etree.SubElement(self.sentence, "token")
        token.set("id", str(word.idx))
        token.set("form", word.corr)

        # Morphology
        if hasattr(word, "pos") and not word.is_cardinal_number():
            token.set("part-of-speech", word.part_of_speech)
            token.set("morphology", word.morphology)
        if hasattr(word, "lemma"):
            token.set("lemma", str(word.lemma).lower())

        # Punctuation
        if row.pcl:
            token.set("presentation-before", row.pcl)
        token.set("presentation-after", " " if row.pcr is None else f"{row.pcr} ")

        # Increment token counter
        self.token_id += 1

        if row.pcr is not None and row.pcr in (".", ":", ";"):
            self.sentence = self._new_sentence()

    def __exit__(self, exc_type, exc_val, exc_tb):
        etree.ElementTree(self.root).write(
            str(self.path), encoding="utf-8", xml_declaration=True, pretty_print=True
        )
