from pathlib import Path
import yaml

# Do not remove this line: necessary for manuscript config construction
from models.manuscript import Manuscript


# Dictionary mapping manuscript IDs to respective data class objects
with Path.joinpath(Path(__file__).resolve().parents[2], "resources", "manuscripts.yaml").open(
    encoding="utf-8"
) as fileobject:
    manuscripts = yaml.load(fileobject.read(), Loader=yaml.Loader)
