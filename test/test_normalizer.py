from functools import partial

import pytest

from components.normalizer.normalizer import Normalizer
from models.word import ParsedWord

parsed = partial(ParsedWord, "DGlush")


@pytest.mark.parametrize(
    "word,norm",
    [
        (parsed("*IС(с)А", ["сущ", "o", "вин/род", "ед", "м", ""]), "ИИСУСА"),
        (parsed("*IС(с)ОВD", ["прил", "a", "вин", "ед", "ж", ""]), "ИИСУСОВУ"),
        (parsed("М(с)ЦА", ["сущ", "jo", "род", "ед", "м", ""]), "МЕСЯЦА"),
        (
            parsed("ПРПW(ДО)&БНАГО", ["прил", "тв", "род", "ед", "м", ""]),
            "ПРЕПОДОБНАГО",
        ),
        (parsed("БЛ(с)ВИ", ["гл", "повел", "2", "ед", "4", ""]), "БЛАГОСЛОВИ"),
    ],
)
def test_normalizer(word, norm):
    assert Normalizer.normalize(word) == norm


@pytest.mark.parametrize(
    "word,norm",
    [(parsed("*ЛАВЪ&РЕНТIЮ", ["сущ", "jo", "дат", "ед", "м", ""]), "ЛАВРЕНТИЮ")],
)
def test_yer_removal_before_linebreak(word, norm):
    assert Normalizer.normalize(word) == norm
