from functools import partial

import pytest

from src.models.word import Word
from src.components.normalizer.normalizer import Normalizer


Word = partial(Word, "DGlush")


@pytest.mark.parametrize(
    "word,norm",
    [
        (Word("*IС(с)А", ["сущ", "o", "вин/род", "ед", "м", ""]), "ИИСУСА"),
        (Word("*IС(с)ОВD", ["прил", "a", "вин", "ед", "ж", ""]), "ИИСУСОВУ"),
    ],
)
def test_normalizer(word, norm):
    assert Normalizer.normalize(word) == norm


@pytest.mark.parametrize(
    "word,norm",
    [(Word("*ЛАВЪ&РЕНТIЮ", ["сущ", "jo", "дат", "ед", "м", ""]), "ЛАВРЕНТИЮ")],
)
def test_yer_removal_before_linebreak(word, norm):
    assert Normalizer.normalize(word) == norm
