from pathlib import Path

from models.row import Row
from .txt_writer import TXTWriter


class TSVWriter(TXTWriter):
    def __init__(self, path: Path):
        super().__init__(path)
        self.stream = Path.open(path, mode="w", encoding="utf-8")

    def write_row(self, row: Row):
        self.stream.write(
            f"{row.tsv()}\t{row.word.lemma if row.word is not None else ''}\n"
        )
