import pytest
from titlegene.services.session_store import SessionStore, LoopLimitError


@pytest.fixture
def store():
    return SessionStore()


def test_create_session_returns_id(store):
    sid = store.create_session()
    assert isinstance(sid, str) and len(sid) > 0


def test_create_session_unique(store):
    assert store.create_session() != store.create_session()


def test_get_history_empty_on_new_session(store):
    sid = store.create_session()
    assert store.get_history(sid) == []


def test_set_and_get_history(store):
    sid = store.create_session()
    msgs = [{"role": "user", "content": "안녕"}]
    store.set_history(sid, msgs)
    assert store.get_history(sid) == msgs


def test_loop_count_starts_at_zero(store):
    sid = store.create_session()
    assert store.get_loop_count(sid) == 0


def test_increment_loop(store):
    sid = store.create_session()
    store.increment_loop(sid)
    assert store.get_loop_count(sid) == 1


def test_increment_loop_twice(store):
    sid = store.create_session()
    store.increment_loop(sid)
    store.increment_loop(sid)
    assert store.get_loop_count(sid) == 2


def test_increment_loop_over_limit_raises(store):
    sid = store.create_session()
    store.increment_loop(sid)
    store.increment_loop(sid)
    with pytest.raises(LoopLimitError):
        store.increment_loop(sid)


def test_unknown_session_history_raises(store):
    with pytest.raises(KeyError):
        store.get_history("nonexistent")


def test_unknown_session_loop_raises(store):
    with pytest.raises(KeyError):
        store.get_loop_count("nonexistent")
