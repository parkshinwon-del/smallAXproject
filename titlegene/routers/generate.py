from fastapi import APIRouter, HTTPException

from titlegene.models.schemas import (
    AnalyzeRequest, AnalyzeResponse,
    TitleRequest, TitleResponse,
    DiffRequest, DiffResponse,
    RefineRequest, RefineResponse,
)
from titlegene.services.session_store import SessionStore, LoopLimitError
from titlegene.services.claude_service import ClaudeService, ClaudeAPIError

router = APIRouter(prefix="/api")
#기능별로 파일을 나눠서 라우터를 만들고 나중에 합쳐요.
#prefix="/api"는 이 라우터 안에서 만드는 모든 경로 앞에 자동으로 /api를 붙인다는 뜻

session_store = SessionStore()
#SessionStore 클래스의 **인스턴스(실제 객체)**를 하나 만드는 거
claude_service = ClaudeService(session_store)
#ClaudeService라는 객체도 하나 만드는데, 방금 만든 session_store를 생성자 인자로 넘겨줘요.


def _require_session(session_id: str) -> None:
    try:
        session_store.get_history(session_id)
        #ession_store에서 해당 session_id의 기록을 꺼내봐요.
        #여기서 실제로 기록을 쓰려는 게 아니에요. 그냥 "이 ID가 존재하냐?"를 확인하는 용도로 호출하는 거예요.
    except KeyError:
        raise HTTPException(status_code=404, detail=f"세션을 찾을 수 없습니다: {session_id}")


@router.post("/analyze", response_model=AnalyzeResponse)
#POST /api/analyze URL로 요청이 오면 이 함수를 실행해라는 선언
#response_model=AnalyzeResponse는 "응답은 반드시 이 모양으로 내보내라"

async def analyze(req: AnalyzeRequest):
    #req에는 사용자가 보낸 요청 데이터가 담겨요.

    sid = session_store.create_session()
    #새 세션을 생성하고 고유한 ID(UUID)를 받아요.
    #이 ID가 이후 모든 대화의 열쇠가 돼요
    try:
        report = claude_service.analyze(sid, req.product_name, req.content, req.target)
    except ClaudeAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return AnalyzeResponse(session_id=sid, report_text=report)
#session_id와 분석 결과(report_text)를 JSON으로 응답해요.
      #클라이언트는 이 session_id를 저장해뒀다가 다음 요청에 사용해요.

@router.post("/generate-title", response_model=TitleResponse)
async def generate_title(req: TitleRequest):

    #POST /api/generate-title로 요청이 오면 실행돼요.
    #req에는 session_id가 담겨 있어요.
    _require_session(req.session_id)
    #이 한 줄이 analyze와의 핵심 차이점이에요.
    #"이 session_id가 진짜 존재하냐?" 먼저 확인해요. 없으면 여기서 바로 404 반환하고 아래 코드는 실행 안 해요.

    try:
        title = claude_service.generate_title(req.session_id)
    except ClaudeAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return TitleResponse(session_id=req.session_id, title_text=title)


@router.post("/differentiate", response_model=DiffResponse)
async def differentiate(req: DiffRequest):
    #req에는 session_id만 담겨 있어요. 제품 정보를 다시 보낼 필요 없이, 세션에 이미 다 저장돼 있거든요.
    _require_session(req.session_id)
    #세션이 존재하는지 먼저 확인해요. 없으면 404 반환하고 종료.
    try:
        diff = claude_service.differentiate(req.session_id)
    #Claude에게 차별화 요청을 해요. 내부적으로는:
#세션에서 지금까지의 대화 기록을 꺼내고
#"이 제목을 경쟁사와 차별화되게 바꿔줘"를 메시지로 추가해서
#Claude API를 호출해요
    except ClaudeAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return DiffResponse(session_id=req.session_id, diff_title=diff)


@router.post("/refine", response_model=RefineResponse)
#POST /api/refine으로 요청이 오면 실행돼요.
#RefineRequest는 session_id + feedback 두 필드예요. 
# 사용자가 "좀 더 친근하게 바꿔줘" 같은 피드백을 함께 보내는 거예요.
async def refine(req: RefineRequest):
    _require_session(req.session_id)
    try:
        refined = claude_service.refine(req.session_id, req.feedback)
    except LoopLimitError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ClaudeAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return RefineResponse(session_id=req.session_id, refined_title=refined)
