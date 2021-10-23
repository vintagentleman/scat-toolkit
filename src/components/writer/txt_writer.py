from pathlib import Path
from typing import List

from models.row import Row
from .writer import Writer


class TXTWriter(Writer):
    def __init__(self, path: Path):
        super().__init__(path)
        self.stream = Path.open(path, mode="w", encoding="utf-8")

    def write_row(self, row: Row):
        self.stream.write(str(row) + " ")

    def write_chunk(self, chunk: List[Row]):
        super().write_chunk(chunk)
        self.stream.write("\n")
