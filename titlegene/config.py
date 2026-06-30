import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
MODEL: str = os.getenv("MODEL", "claude-sonnet-4-6")
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))
MAX_LOOP_COUNT: int = 2


def validate() -> None:
    """서버 시작 시 필수 환경변수 검증. 누락이면 SystemExit."""
    import sys
    if not ANTHROPIC_API_KEY:
        print("[TitleGen] ERROR: ANTHROPIC_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.", file=sys.stderr)
        sys.exit(1)
