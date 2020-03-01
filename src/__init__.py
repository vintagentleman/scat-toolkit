import json
from pathlib import Path

__root__ = Path(__file__).resolve().parents[1]

__metadata__ = json.load(
    Path.joinpath(__root__, "conf", "meta.json").open(encoding="utf-8")
)
