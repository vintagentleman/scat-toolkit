import shelve
from pathlib import Path

from components.pickler import Pickler
from models.row import Row

from .writer import Writer


class PKLWriter(Writer):
    def __init__(self, path: Path):
        super().__init__(path)
        self.stream = shelve.open(str(path), writeback=True)

    def write_row(self, row: Row):
        word = row.word
        if word is None or word.tagset is None or word.lemma is None:
            return

        tagsets = self.stream.setdefault(word.norm, [])

        if (pickled := Pickler.pickle(word.tagset, word.lemma)) not in tagsets:
            tagsets.append(pickled)
