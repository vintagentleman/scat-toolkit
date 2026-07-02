import pytest

from models.tagset import tagset_factory
from models.tagset.noun_tagset import NounTagset
from models.tagset.participle_tagset import ParticipleTagset
from models.tagset.pronoun_tagset import PronounTagset
from models.tagset.tagset import Tagset
from models.tagset.verb_tagset import VerbTagset


@pytest.mark.parametrize(
    "columns, cls",
    [
        (["сущ", "jo", "род", "ед", "м", ""], NounTagset),
        (["прил", "тв", "род", "ед", "м", ""], NounTagset),  # adjectives -> NounTagset
        (["прил/ср", "ja", "вин", "ед", "ж", ""], NounTagset),  # comparatives too
        (["мест", "м", "род", "ед", "м", ""], NounTagset),  # non-personal pronoun
        (["мест", "личн", "2", "дат", "ед", ""], PronounTagset),  # personal pronoun
        (["прич", "м", "прош", "род", "мн", "м"], ParticipleTagset),
        (["гл", "повел", "2", "ед", "4", ""], VerbTagset),
        (["11"], Tagset),  # cardinal number -> bare Tagset
        (["союз"], Tagset),  # indeclinable -> bare Tagset
    ],
)
def test_tagset_factory_dispatch(columns, cls):
    assert type(tagset_factory(columns)) is cls


@pytest.mark.parametrize(
    "columns, expected",
    [
        (["сущ", "jo", "род", "ед", "м", ""], "jo;род;ед;м"),
        (["прил", "тв", "род", "ед", "м", ""], "тв;род;ед;м"),
        (["мест", "личн", "2", "дат", "ед", ""], "2;дат;ед"),
        (["прич", "м", "прош", "род", "мн", "м"], "м;прош;род;мн;м;акт"),
        (["гл", "повел", "2", "ед", "4", ""], "повел;ед;2;4"),
    ],
)
def test_tagset_str(columns, expected):
    assert str(tagset_factory(columns)) == expected


def test_noun_keeps_factual_case_for_syncretic_accusative():
    # "вин/род" (accusative realised as genitive) stores the factual (genitive) case
    assert tagset_factory(["сущ", "o", "вин/род", "ед", "м", ""]).case == "род"


@pytest.mark.parametrize(
    "columns, expected",
    [
        (["сущ", "o", "вин/род", "ед", "м", ""], "o;род;ед;м;одуш"),
        (["мест", "личн", "1", "вин/род", "ед"], "1;род;ед;одуш"),
        (["прич", "a", "прош", "вин/род", "ед", "м"], "a;прош;род;ед;м;пас;одуш"),
    ],
)
def test_animacy_tag_appended_for_accusative_genitive_syncretism(columns, expected):
    # "вин/род" surfaces the "одуш" animacy tag that the factual-case collapse would otherwise drop
    tagset = tagset_factory(columns)
    assert tagset.animate == "одуш"
    assert str(tagset) == expected


@pytest.mark.parametrize(
    "declension, voice",
    [("a", "пас"), ("o", "пас"), ("тв", "пас"), ("м", "акт"), ("en", "акт")],
)
def test_participle_voice_inferred_from_declension(declension, voice):
    tagset = tagset_factory(["прич", declension, "прош", "им", "ед", "м"])
    assert tagset.voice == voice
