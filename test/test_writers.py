from lxml import etree

from components.lemmatizer import lemmatizer_factory
from components.normalizer.normalizer import Normalizer
from components.writer import writer_factory
from data.manuscripts import manuscripts
from models.row import WordRow, XMLRow
from models.word import Word

TEI_NS = {"t": "http://www.tei-c.org/ns/1.0"}


def build_row(columns):
    row = WordRow("DmPrlc", columns)
    parsed = row.parsed_word
    norm = Normalizer.normalize(parsed)
    lemma = lemmatizer_factory(parsed).lemmatize(parsed, norm)
    row.word = Word(parsed, norm, lemma)
    return row


def test_tsv_writer_appends_lemma(tmp_path):
    columns = ["М(с)ЦА", "сущ", "jo", "род", "ед", "м", ""]
    out = tmp_path / "DmPrlc.tsv"
    with writer_factory("tsv", out) as writer:
        writer.write_row(build_row(columns))

    fields = out.read_text(encoding="utf-8").splitlines()[0].split("\t")
    assert fields[:7] == columns
    assert fields[7] == "месяць"  # lower-cased by the Word lemma setter


def test_xml_writer_emits_tei_word(tmp_path):
    out = tmp_path / "DmPrlc.xml"
    with writer_factory("xml", out) as writer:
        writer.write_chunk([build_row(["М(с)ЦА", "сущ", "jo", "род", "ед", "м", ""])])

    word = etree.parse(str(out)).find(".//t:w", TEI_NS)
    assert word.get("pos") == "сущ"
    assert word.get("msd") == "jo;род;ед;м"
    assert word.get("norm") == "МЕСЯЦА"
    assert word.get("lemma") == "месяць"


def test_tt_writer_emits_annatto_compatible_rows(tmp_path):
    manuscript = manuscripts["DmPrlc"]
    previous_token_id = manuscript._token_id
    manuscript.token_id = 0

    try:
        rows = [
            XMLRow("DmPrlc", ['<head n="1">'] + [""] * 6),
            build_row(["М(с)ЦА,", "сущ", "jo", "род", "ед", "м", ""]),
            build_row(["Д#", "4", "", "", "", "", ""]),
            XMLRow("DmPrlc", ["</head>"] + [""] * 6),
        ]

        out = tmp_path / "DmPrlc.tt"
        with writer_factory("tt", out) as writer:
            for row in rows:
                writer.write_row(row)
    finally:
        manuscript._token_id = previous_token_id

    assert out.read_text(encoding="utf-8").splitlines() == [
        '<doc id="DmPrlc" title="Житие Димитрия Прилуцкого" century="16" morphology="true" text_structure="true">',
        '<head n="1">',
        "м҇ⷭца\tсущ\tjo;род;ед;м\tмесяць\tМЕСЯЦА\tDmPrlc.1",
        '<num value="4">',
        ",\t \t \t \t \tDmPrlc.2",
        "д҃\t \t \t4\t4\tDmPrlc.3",
        "</num>",
        "</head>",
        "</doc>",
    ]


def test_tt_writer_does_not_treat_tokenizer_numbers_as_morphology(tmp_path):
    manuscript = manuscripts["DmPrlc"]
    previous_token_id = manuscript._token_id
    manuscript.token_id = 0

    try:
        out = tmp_path / "DmPrlc.tt"
        with writer_factory("tt", out) as writer:
            writer.write_row(build_row(["Д#", "4", "", "", "", "", ""]))
    finally:
        manuscript._token_id = previous_token_id

    header = out.read_text(encoding="utf-8").splitlines()[0]
    assert 'morphology="false"' in header
    assert 'text_structure="false"' in header
