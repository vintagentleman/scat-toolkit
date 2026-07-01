from pathlib import Path

import yaml

# Registers the "!Manuscript" YAML tag as an import side effect; do not remove.
from models.manuscript import Manuscript  # noqa: F401

# Dictionary mapping manuscript IDs to respective data class objects
with Path.joinpath(
    Path(__file__).resolve().parents[2], "resources", "manuscripts.yaml"
).open(encoding="utf-8") as fileobject:
    manuscripts = yaml.load(fileobject.read(), Loader=yaml.Loader)
