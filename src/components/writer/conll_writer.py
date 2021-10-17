from pathlib import Path
from typing import List

from models.row import Row
from .writer import Writer


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
