from pathlib import Path

import pytest

import converter

SAMPLE = Path("scat-content/annotation/morphological/DmPrlc.tsv")

pytestmark = pytest.mark.skipif(
    not SAMPLE.exists(), reason="scat-content submodule not checked out"
)


def test_convert_real_sample_normalises_and_lemmatises(tmp_path):
    slice_ = tmp_path / "DmPrlc.tsv"
    lines = SAMPLE.read_text(encoding="utf-8").splitlines()[:15]
    slice_.write_text("\n".join(lines) + "\n", encoding="utf-8")

    text = converter.Text(slice_)
    text.parse_rows()

    assert text.rows
    first = text.rows[0].word
    assert first.norm == "МЕСЯЦА"
    assert first.lemma == "месяць"
