from abc import abstractmethod
from contextlib import AbstractContextManager
from pathlib import Path
from typing import List

from models.row import Row
from src import manuscripts


class Writer(AbstractContextManager):
    @abstractmethod
    def __init__(self, path: Path):
        self.path = path
        self.manuscript = manuscripts.get(path.stem)
        self.stream = NotImplemented

    @abstractmethod
    def write_row(self, row: Row):
        pass

    def write_chunk(self, chunk: List[Row]):
        [self.write_row(row) for row in chunk]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stream.close()
