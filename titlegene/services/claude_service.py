import anthropic

from titlegene import config
from titlegene.services.session_store import SessionStore
from titlegene.services.prompt_service import PromptService


class ClaudeAPIError(Exception):
    """Claude API 호출 실패 시 발생."""


class ClaudeService:
    def __init__(self, session_store: SessionStore) -> None:
        self._store = session_store
        self._client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def _call_api(self, session_id: str, user_message: str) -> str:
        history = self._store.get_history(session_id)
        history.append({"role": "user", "content": user_message})
        try:
            response = self._client.messages.create(
                model=config.MODEL,
                max_tokens=config.MAX_TOKENS,
                messages=history,
            )
        except Exception as e:
            # 실패 시 마지막 user 메시지 롤백
            history.pop()
            raise ClaudeAPIError(str(e)) from e

        assistant_text = response.content[0].text
        history.append({"role": "assistant", "content": assistant_text})
        self._store.set_history(session_id, history)
        return assistant_text

    def analyze(self, session_id: str, product_name: str, content: str, target: str) -> str:
        prompt = PromptService.build_analyze_prompt(product_name, content, target)
        return self._call_api(session_id, prompt)

    def generate_title(self, session_id: str) -> str:
        prompt = PromptService.build_title_prompt()
        return self._call_api(session_id, prompt)

    def differentiate(self, session_id: str) -> str:
        prompt = PromptService.build_differentiate_prompt()
        return self._call_api(session_id, prompt)

    def refine(self, session_id: str, feedback: str) -> str:
        prompt = PromptService.build_refine_prompt(feedback)
        return self._call_api(session_id, prompt)
