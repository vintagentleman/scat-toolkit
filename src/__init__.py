from pathlib import Path

import yaml

# Do not remove this line: necessary for manuscript config construction
from models.manuscript import Manuscript

# Project root directory
__root__ = Path(__file__).resolve().parents[1]

# Dictionary mapping manuscript IDs to respective data class objects
with Path.joinpath(__root__, "resources", "manuscripts.yaml").open(
    encoding="utf-8"
) as fileobject:
    manuscripts = yaml.load(fileobject.read(), Loader=yaml.Loader)
