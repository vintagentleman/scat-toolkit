from dataclasses import dataclass

from yaml import YAMLObject


@dataclass
class Manuscript(YAMLObject):
    yaml_tag = "!Manuscript"

    title: str
    page: int
    column: str
    line: int

    # ID counters
    _token_id: int = 0
    _chunk_id: int = 0

    @property
    def token_id(self):
        self._token_id += 1
        return self._token_id

    @token_id.setter
    def token_id(self, value):
        self._token_id = value

    @property
    def chunk_id(self):
        self._chunk_id += 1
        return self._chunk_id

    @chunk_id.setter
    def chunk_id(self, value):
        self._token_id = value
