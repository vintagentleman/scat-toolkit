from dataclasses import dataclass

from yaml import YAMLObject


@dataclass
class Manuscript(YAMLObject):
    yaml_tag = "!Manuscript"

    title: str
    page: int
    column: str
    line: int

    # Token ID counter
    _token_id: int = 0

    @property
    def token_id(self):
        self._token_id += 1
        return self._token_id
