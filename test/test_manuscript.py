from models.manuscript import Manuscript


def make_manuscript():
    return Manuscript(title="Test", page=1, column="", line=1)


def test_chunk_id_setter_sets_chunk_id():
    m = make_manuscript()
    m.chunk_id = 10
    # The getter increments before returning, so the next read is value + 1.
    assert m.chunk_id == 11


def test_chunk_id_setter_leaves_token_id_untouched():
    m = make_manuscript()
    m.token_id = 5
    m.chunk_id = 10
    assert m.token_id == 6
