import uuid
from typing import Any

MAX_LOOP = 2


class LoopLimitError(Exception):
    """피드백 루프 횟수(MAX_LOOP=2) 초과 시 발생."""


class SessionStore:
    def __init__(self) -> None:
        self._history: dict[str, list[dict[str, Any]]] = {}
        self._loop_count: dict[str, int] = {}

    def create_session(self) -> str:
        sid = str(uuid.uuid4())
        self._history[sid] = []
        self._loop_count[sid] = 0
        return sid

    def get_history(self, session_id: str) -> list[dict[str, Any]]:
        if session_id not in self._history:
            raise KeyError(f"세션을 찾을 수 없습니다: {session_id}")
        return self._history[session_id]

    def set_history(self, session_id: str, history: list[dict[str, Any]]) -> None:
        if session_id not in self._history:
            raise KeyError(f"세션을 찾을 수 없습니다: {session_id}")
        self._history[session_id] = history

    def get_loop_count(self, session_id: str) -> int:
        if session_id not in self._loop_count:
            raise KeyError(f"세션을 찾을 수 없습니다: {session_id}")
        return self._loop_count[session_id]

    def increment_loop(self, session_id: str) -> None:
        if session_id not in self._loop_count:
            raise KeyError(f"세션을 찾을 수 없습니다: {session_id}")
        if self._loop_count[session_id] >= MAX_LOOP:
            raise LoopLimitError(f"피드백 최대 횟수({MAX_LOOP}회)를 초과했습니다.")
        self._loop_count[session_id] += 1
