---
title: TitleGen Architecture Spine
status: final
created: 2026-06-29
updated: 2026-06-29
---

# TitleGen — 아키텍처 스파인

## 설계 패러다임

**레이어드 모놀리스 (Layered Monolith)**
단일 Python 서버 내에서 Router → Service → External API 의 단방향 의존 계층을 고정한다.
1인 사용, 세션 내 상태만 유지하는 규모에 맞는 가장 단순한 구조다.

---

## AD-1 백엔드 프레임워크 — FastAPI

**Rule:** 백엔드는 FastAPI(Python)로 구현한다.
**Binds:** 모든 엔드포인트는 `async def`로 선언하고 Pydantic 스키마로 요청/응답을 검증한다.
**Prevents:** Flask 혼용, 동기 blocking I/O로 Claude API 호출하는 것.

---

## AD-2 컨텍스트 누적 전략 — 단일 messages 배열

**Rule:** Phase 2 → 3 → 4 → 5(피드백)의 Claude API 호출은 모두 하나의 `messages` 배열에 이전 응답을 순서대로 쌓아서 전달한다.

```python
# ClaudeService._call_api 핵심 패턴
history = session_store.get_history(session_id)
history.append({"role": "user", "content": user_message})
response = client.messages.create(
    model=config.MODEL,
    messages=history,          # 누적 전체 전달
    max_tokens=config.MAX_TOKENS,
)
assistant_msg = response.content[0].text
history.append({"role": "assistant", "content": assistant_msg})
session_store.set_history(session_id, history)
```

**Binds:** 모든 Claude 호출은 `ClaudeService._call_api()` 를 통해서만 이루어진다.
**Prevents:** 각 엔드포인트가 독립적으로 Claude client를 직접 호출하는 것.

---

## AD-3 API 키 보안 — 서버 사이드 환경변수

**Rule:** `ANTHROPIC_API_KEY` 는 `.env` 파일에만 저장하고, 클라이언트(브라우저)에 절대 노출하지 않는다.

**Binds:** `config.py` 가 `python-dotenv` 로 환경변수를 로드하고, 라우터/프론트엔드는 키에 직접 접근하지 않는다.
**Prevents:** 프론트엔드 JS 코드에 API 키 하드코딩.

---

## AD-4 피드백 루프 제한 — SessionStore에서 단일 관리

**Rule:** 루프 횟수 제한(`MAX_LOOP = 2`)은 `SessionStore` 가 단독으로 소유한다. 라우터는 `SessionStore.get_loop_count()` 를 조회하고, 초과 시 HTTP 400을 반환한다.

**Binds:** 루프 카운트 증가는 `SessionStore.increment_loop()` 만 호출한다.
**Prevents:** 프론트엔드에서 횟수를 세거나, 각 라우터 함수가 독립적으로 카운트를 관리하는 것.

---

## AD-5 시스템 프롬프트 소유권 — PromptService 집중 관리

**Rule:** 사용자에게 노출되지 않는 자동 추가 문구(제목 규칙, 차별화 지시 등)는 모두 `PromptService` 상수로 정의하고, `ClaudeService` 가 호출 시 조합한다.

**Binds:**
- 제목 생성 프롬프트: `"핵심 상품명이 제목 맨 앞쪽에 나올수록 좋다. 제목은 15글자 미만으로 쓰기."` + `"타겟의 특성이 일치하는 SNS 유행 콘텐츠의 어조 쓰기"`
- 차별화 프롬프트: `"위 제목을 차별화해줘. 기준은 네이버 상위노출 페이지에 나오는 콘텐츠 제목과 달라야 돼"`

**Prevents:** 프롬프트 문자열이 라우터 또는 프론트엔드에 분산되는 것.

---

## AD-6 세션 상태 — 인메모리 딕셔너리

**Rule:** 대화 히스토리와 루프 카운트는 `SessionStore` 의 Python 딕셔너리(`dict`)에 보관한다. 영구 저장소(DB, 파일)는 사용하지 않는다.

**Binds:** 서버 재시작 시 모든 세션 데이터는 초기화된다.
**Prevents:** Redis, SQLite 등 외부 세션 스토어 도입(초기 버전 범위 초과).

---

## Python 모듈 구조

```
titlegene/
├── main.py                  # FastAPI 앱 생성, 라우터 등록, CORS 설정
├── config.py                # 환경변수 로드 (ANTHROPIC_API_KEY, MODEL, MAX_LOOP_COUNT)
├── routers/
│   └── generate.py          # 4개 엔드포인트: /analyze, /generate-title, /differentiate, /refine
├── services/
│   ├── claude_service.py    # Claude API 호출 & 누적 컨텍스트 관리 (AD-2)
│   ├── prompt_service.py    # 시스템 프롬프트 상수 & 조합 (AD-5)
│   └── session_store.py     # 인메모리 세션 & 루프 카운트 (AD-4, AD-6)
├── models/
│   └── schemas.py           # Pydantic 요청/응답 모델
├── static/
│   └── index.html           # 단일 페이지 프론트엔드 (HTML + Vanilla JS)
├── .env                     # ANTHROPIC_API_KEY (git 제외)
├── .env.example             # 키 제외 템플릿
└── requirements.txt
```

---

## 데이터 플로우 — API 엔드포인트

| 엔드포인트 | 입력 | Claude 호출 | 출력 |
|-----------|------|------------|------|
| `POST /api/analyze` | session_id, product_name, content, target | #1 (새 history) | report_text |
| `POST /api/generate-title` | session_id | #2 (누적) + 제목 프롬프트 자동 추가 | title_text |
| `POST /api/differentiate` | session_id | #3 (누적) + 차별화 프롬프트 자동 추가 | diff_title |
| `POST /api/refine` | session_id, feedback, loop_count | #4/#5 (누적) — loop_count≥2 시 400 반환 | refined_title |

---

## UML 다이어그램

| 파일 | 내용 |
|------|------|
| `sequence_*.svg` | 전체 동작 플로우 (사용자 → 프론트 → 백엔드 → ClaudeService → Claude API) |
| `class_*.svg` | Python 모듈 구조 및 의존 관계 |
| `activity_*.svg` | Phase별 흐름 및 피드백 루프 분기 |

---

## 배포 구조

```
인터넷
  ↓ HTTPS (443)
[Nginx / Reverse Proxy]
  ↓ HTTP (8000)
[Uvicorn + FastAPI]   ← .env (API 키)
  ↓ HTTPS
[Claude API - Anthropic]
```

- **서버:** VPS 또는 클라우드 인스턴스 (예: AWS EC2, Railway, Render)
- **프로세스:** `uvicorn titlegene.main:app --host 0.0.0.0 --port 8000`
- **HTTPS:** Nginx + Let's Encrypt (Certbot) 또는 배포 플랫폼 자동 적용

---

## Deferred (이 버전에서 결정하지 않음)

| 항목 | 조건 |
|------|------|
| 다중 사용자 세션 격리 | 사용자 수 증가 시 Redis 세션 도입 고려 |
| API 호출 횟수 Rate Limiting | 비용 이슈 발생 시 |
| 결과 히스토리 영구 저장 | 사용자 요청 시 DB 도입 |
| 프롬프트 사용자 커스터마이징 | v2 요구사항 |
