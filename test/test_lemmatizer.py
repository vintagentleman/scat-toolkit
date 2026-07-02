import pytest

from components.lemmatizer import lemmatizer_factory
from components.normalizer.normalizer import Normalizer
from models.row import WordRow


def lemma_of(columns):
    word = WordRow("DmPrlc", columns).word
    word.norm = Normalizer.normalize(word)
    return lemmatizer_factory(word).lemmatize(word)


@pytest.mark.parametrize(
    "columns, expected",
    [
        (["М(с)ЦА", "сущ", "jo", "род", "ед", "м", ""], "МЕСЯЦЬ"),
        (["ПРПW(ДО)&БНАГО", "прил", "тв", "род", "ед", "м", ""], "ПРЕПОДОБНЫИ"),
        (["БОЛШU", "прил/ср", "ja", "вин", "ед", "ж", ""], "БОЛИИ"),
        (["НШЕГО#", "мест", "м", "род", "ед", "м", ""], "НАШЬ"),
        (["ТЕБ+,", "мест", "личн", "2", "дат", "ед", ""], "ТЫ"),
        (["БЛ(с)ВИ", "гл", "повел", "2", "ед", "4", ""], "БЛАГОСЛОВИТИ"),
        (["UДИВИШАСR,", "гл/в", "изъяв", "аор гл", "3", "мн", ""], "УДИВИТИСЯ"),
        (["ПОЖИВШИ(Х),", "прич", "м", "прош", "род", "мн", "м"], "ПОЖИТИ"),
    ],
)
def test_lemmatize(columns, expected):
    assert lemma_of(columns) == expected
