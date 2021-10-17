from pathlib import Path

from .writer import Writer
from .txt_writer import TXTWriter
from .tsv_writer import TSVWriter
from .pkl_writer import PKLWriter
from .xml_writer import XMLWriter
from .conll_writer import CoNLLWriter


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
