import shelve
from pathlib import Path

from models.row import Row
from .writer import Writer
from components.pickler import Pickler


class PKLWriter(Writer):
    def __init__(self, path: Path):
        super().__init__(path)
        self.stream = shelve.open(str(path), writeback=True)

    def write_row(self, row: Row):
        if row.word is None or row.word.tagset is None:
            return

        tagsets = self.stream.setdefault(row.word.norm, [])

        if (pickled := Pickler.pickle(row.word)) not in tagsets:
            tagsets.append(pickled)
