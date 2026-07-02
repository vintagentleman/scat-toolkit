from pathlib import Path

from .pkl_writer import PKLWriter
from .tsv_writer import TSVWriter
from .txt_writer import TXTWriter
from .writer import Writer
from .xml_writer import XMLWriter


def writer_factory(mode: str, path: Path) -> Writer:
    if mode == "txt":
        return TXTWriter(path)
    if mode == "tsv":
        return TSVWriter(path)
    if mode == "pkl":
        return PKLWriter(path)
    if mode == "xml":
        return XMLWriter(path)
    raise NotImplementedError
