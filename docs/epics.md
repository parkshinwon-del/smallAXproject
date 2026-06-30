# TitleGen — Epics & Stories

## Epic 1: 프로젝트 기반 설정 (Project Foundation)

백엔드 실행 환경, 의존성, 설정 모듈을 갖춘 FastAPI 프로젝트 골격을 세운다.

### Story 1.1: 프로젝트 스캐폴딩 및 의존성 설치
requirements.txt, .env.example, main.py(FastAPI 앱), config.py(환경변수 로드)를 작성한다.

**AC:**
- `uvicorn titlegene.main:app` 실행 시 서버가 정상 기동된다.
- `GET /health` → `{"status":"ok"}` 반환.
- `ANTHROPIC_API_KEY` 누락 시 시작 시점에 명확한 오류 메시지.

### Story 1.2: Pydantic 요청/응답 스키마 정의
`models/schemas.py`에 4개 엔드포인트의 요청·응답 Pydantic 모델을 작성한다.

**AC:**
- `AnalyzeRequest`, `TitleRequest`, `DiffRequest`, `RefineRequest` 모델 존재.
- 각 모델 유효성 검증 단위 테스트 통과.
- `session_id` 필드가 모든 요청 모델에 포함.

---

## Epic 2: 세션 및 프롬프트 서비스 (Session & Prompt Services)

인메모리 세션 관리와 시스템 프롬프트 조합 로직을 구현한다.

### Story 2.1: SessionStore 구현
`services/session_store.py` — 대화 히스토리와 루프 카운트를 인메모리 dict로 관리.

**AC:**
- `create_session()` → 새 session_id 반환.
- `get_history()` / `set_history()` 정상 동작.
- `get_loop_count()` / `increment_loop()` 정상 동작.
- `get_loop_count() >= 2` 이면 `increment_loop()`가 `LoopLimitError` 발생.
- 단위 테스트 5개 이상 통과.

### Story 2.2: PromptService 구현
`services/prompt_service.py` — 자동 추가 시스템 프롬프트 상수와 조합 메서드.

**AC:**
- `TITLE_RULES` 상수: `"핵심 상품명이 제목 맨 앞쪽에 나올수록 좋다. 제목은 15글자 미만으로 쓰기."` + `"타겟의 특성이 일치하는 SNS 유행 콘텐츠의 어조 쓰기"` 포함.
- `DIFFERENTIATE_PROMPT` 상수: `"위 제목을 차별화해줘. 기준은 네이버 상위노출 페이지에 나오는 콘텐츠 제목과 달라야 돼"` 포함.
- `build_analyze_prompt()`, `build_title_prompt()`, `build_differentiate_prompt()`, `build_refine_prompt()` 메서드 존재.
- 단위 테스트: 각 메서드 반환 문자열에 필수 문구 포함 여부 검증.

---

## Epic 3: Claude API 통합 (Claude Service)

ClaudeService가 누적 컨텍스트를 유지하며 Claude API를 호출한다.

### Story 3.1: ClaudeService 구현
`services/claude_service.py` — `_call_api()` 핵심 메서드와 Phase별 호출 래퍼.

**AC:**
- `_call_api(session_id, user_message)` → messages 배열에 누적하여 Claude API 호출.
- `analyze()`, `generate_title()`, `differentiate()`, `refine()` 래퍼 메서드 존재.
- API 응답 텍스트를 `assistant` 롤로 history에 추가 후 반환.
- `httpx.HTTPError` 발생 시 `ClaudeAPIError` re-raise.
- 단위 테스트: mock API로 누적 컨텍스트 전달 검증.

---

## Epic 4: API 엔드포인트 (FastAPI Routers)

4개 엔드포인트를 라우터로 구현하고 루프 제한을 적용한다.

### Story 4.1: /api/analyze 엔드포인트
`routers/generate.py` — Phase 2 타겟 분석 보고서 엔드포인트.

**AC:**
- `POST /api/analyze` → `AnalyzeRequest` 수신, `ClaudeService.analyze()` 호출, `{"report_text": "..."}` 반환.
- 신규 session_id 자동 생성 및 반환.
- Claude API 오류 → HTTP 502 반환.

### Story 4.2: /api/generate-title 엔드포인트
Phase 3 제목 생성 엔드포인트.

**AC:**
- `POST /api/generate-title` → `{"title_text": "..."}` 반환.
- 누적 컨텍스트(Phase 2 결과) 포함 확인.
- 존재하지 않는 session_id → HTTP 404.

### Story 4.3: /api/differentiate 엔드포인트
Phase 4 제목 차별화 엔드포인트.

**AC:**
- `POST /api/differentiate` → `{"diff_title": "..."}` 반환.
- 누적 컨텍스트(Phase 2+3 결과) 포함 확인.

### Story 4.4: /api/refine 엔드포인트 (루프 제한 포함)
Phase 5 피드백 재생성 엔드포인트.

**AC:**
- `POST /api/refine` → `{"refined_title": "..."}` 반환.
- `loop_count >= 2` 이면 HTTP 400 + `{"detail":"피드백 횟수 초과"}` 반환.
- 성공 시 loop_count 1 증가.

---

## Epic 5: 프론트엔드 (Single Page Frontend)

`static/index.html` — Phase 1~5 전체 흐름을 단일 HTML + Vanilla JS로 구현.

### Story 5.1: Phase 1 UI — 데이터 수집 폼
입력 폼(콘텐츠·상품명·타겟)과 데이터랩 안내 박스.

**AC:**
- 콘텐츠 textarea, 상품명 input, 타겟 input 렌더링.
- 데이터랩 링크가 새 탭으로 열림.
- 입력값이 JS 상태(state)에 보존.

### Story 5.2: Phase 2~4 UI — API 호출 버튼 & 결과 표시
분석·생성·차별화 버튼과 결과 텍스트박스.

**AC:**
- 각 버튼 클릭 → 해당 API POST 호출 → 결과 텍스트박스 업데이트.
- 로딩 중 버튼 비활성화 + 스피너.
- API 오류 시 빨간 안내 메시지.

### Story 5.3: Phase 5 UI — 피드백 루프 & 완료 처리
피드백 입력, 재생성 버튼, YES/NO 체크박스, 완료 메시지.

**AC:**
- 재생성 버튼 → `/api/refine` 호출.
- 피드백 2회 초과 시 버튼 비활성화 + 안내 문구.
- NO 선택 시 `"제목이 완성되었습니다!"` 표시.
- YES 선택 시 피드백 입력 폼으로 포커스.

---

## Epic 6: 배포 설정 (Deployment)

서버 배포를 위한 설정 파일 및 문서.

### Story 6.1: 배포 설정 파일 작성
Procfile, nginx.conf 템플릿, requirements.txt 완성.

**AC:**
- `Procfile`: `web: uvicorn titlegene.main:app --host 0.0.0.0 --port 8000`
- `nginx.conf` 템플릿에 HTTPS proxy_pass 설정 포함.
- README.md에 로컬 실행 및 배포 절차 기술.
