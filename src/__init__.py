from pathlib import Path
import yaml


# Project root directory
__root__ = Path(__file__).resolve().parents[1]

# Dictionary mapping manuscript IDs to respective data class objects
with Path.joinpath(__root__, "resources", "manuscripts.yaml").open(
    encoding="utf-8"
) as fileobject:
    manuscripts = yaml.load(fileobject.read(), Loader=yaml.Loader)
