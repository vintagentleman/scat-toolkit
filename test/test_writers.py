from lxml import etree

from components.lemmatizer import lemmatizer_factory
from components.normalizer.normalizer import Normalizer
from components.writer import writer_factory
from models.row import WordRow

TEI_NS = {"t": "http://www.tei-c.org/ns/1.0"}


def build_row(columns):
    row = WordRow("DmPrlc", columns)
    row.word.norm = Normalizer.normalize(row.word)
    row.word.lemma = lemmatizer_factory(row.word).lemmatize(row.word)
    return row


def test_tsv_writer_appends_lemma(tmp_path):
    columns = ["М(с)ЦА", "сущ", "jo", "род", "ед", "м", ""]
    out = tmp_path / "DmPrlc.tsv"
    with writer_factory("tsv", out) as writer:
        writer.write_row(build_row(columns))

    fields = out.read_text(encoding="utf-8").splitlines()[0].split("\t")
    assert fields[:7] == columns
    assert fields[7] == "месяць"  # lemma appended, lowercased by the Word setter


def test_xml_writer_emits_tei_word(tmp_path):
    out = tmp_path / "DmPrlc.xml"
    with writer_factory("xml", out) as writer:
        writer.write_chunk([build_row(["М(с)ЦА", "сущ", "jo", "род", "ед", "м", ""])])

    word = etree.parse(str(out)).find(".//t:w", TEI_NS)  # also asserts well-formed XML
    assert word.get("pos") == "сущ"
    assert word.get("msd") == "jo;род;ед;м"
    assert word.get("norm") == "МЕСЯЦА"
    assert word.get("lemma") == "месяць"
