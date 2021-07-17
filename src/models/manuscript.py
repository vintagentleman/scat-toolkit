from dataclasses import dataclass

from yaml import YAMLObject


@dataclass
class Manuscript(YAMLObject):
    yaml_tag = "!Manuscript"

    title: str
    page: int
    column: str
    line: int
