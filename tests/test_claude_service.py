import pytest
from unittest.mock import MagicMock, patch
from titlegene.services.session_store import SessionStore
from titlegene.services.claude_service import ClaudeService, ClaudeAPIError


@pytest.fixture
def store():
    return SessionStore()


@pytest.fixture
def service(store):
    return ClaudeService(store)


def _mock_response(text: str):
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


def test_analyze_returns_text(service, store):
    sid = store.create_session()
    with patch.object(service._client.messages, "create", return_value=_mock_response("보고서 요약")) as mock_create:
        result = service.analyze(sid, "무릎보호대", "글내용", "50대여성")
    assert result == "보고서 요약"
    mock_create.assert_called_once()


def test_analyze_accumulates_history(service, store):
    sid = store.create_session()
    with patch.object(service._client.messages, "create", return_value=_mock_response("보고서")):
        service.analyze(sid, "무릎보호대", "글내용", "50대여성")
    history = store.get_history(sid)
    assert len(history) == 2  # user + assistant
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "보고서"


def test_generate_title_uses_accumulated_context(service, store):
    sid = store.create_session()
    with patch.object(service._client.messages, "create", return_value=_mock_response("보고서")):
        service.analyze(sid, "무릎보호대", "글내용", "50대여성")
    with patch.object(service._client.messages, "create", return_value=_mock_response("무릎보호대 관절 끝")) as mock_create:
        result = service.generate_title(sid)
    assert result == "무릎보호대 관절 끝"
    # 누적 컨텍스트 확인: 이전 2개 + 새 user 메시지 포함
    called_messages = mock_create.call_args.kwargs["messages"]
    assert len(called_messages) >= 3


def test_differentiate_returns_text(service, store):
    sid = store.create_session()
    with patch.object(service._client.messages, "create", return_value=_mock_response("r")):
        service.analyze(sid, "p", "c", "t")
    with patch.object(service._client.messages, "create", return_value=_mock_response("title")):
        service.generate_title(sid)
    with patch.object(service._client.messages, "create", return_value=_mock_response("차별화 제목")) as m:
        result = service.differentiate(sid)
    assert result == "차별화 제목"


def test_refine_returns_text(service, store):
    sid = store.create_session()
    with patch.object(service._client.messages, "create", return_value=_mock_response("r")):
        service.analyze(sid, "p", "c", "t")
    with patch.object(service._client.messages, "create", return_value=_mock_response("t")):
        service.generate_title(sid)
    with patch.object(service._client.messages, "create", return_value=_mock_response("d")):
        service.differentiate(sid)
    with patch.object(service._client.messages, "create", return_value=_mock_response("개선 제목")):
        result = service.refine(sid, "더 젊게")
    assert result == "개선 제목"


def test_api_error_raises_claude_api_error(service, store):
    sid = store.create_session()
    with patch.object(service._client.messages, "create", side_effect=Exception("API 오류")):
        with pytest.raises(ClaudeAPIError):
            service.analyze(sid, "p", "c", "t")
