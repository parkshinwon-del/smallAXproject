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

session_store = SessionStore()
claude_service = ClaudeService(session_store)


def _require_session(session_id: str) -> None:
    try:
        session_store.get_history(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"세션을 찾을 수 없습니다: {session_id}")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    sid = session_store.create_session()
    try:
        report = claude_service.analyze(sid, req.product_name, req.content, req.target)
    except ClaudeAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return AnalyzeResponse(session_id=sid, report_text=report)


@router.post("/generate-title", response_model=TitleResponse)
async def generate_title(req: TitleRequest):
    _require_session(req.session_id)
    try:
        title = claude_service.generate_title(req.session_id)
    except ClaudeAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return TitleResponse(session_id=req.session_id, title_text=title)


@router.post("/differentiate", response_model=DiffResponse)
async def differentiate(req: DiffRequest):
    _require_session(req.session_id)
    try:
        diff = claude_service.differentiate(req.session_id)
    except ClaudeAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return DiffResponse(session_id=req.session_id, diff_title=diff)


@router.post("/refine", response_model=RefineResponse)
async def refine(req: RefineRequest):
    _require_session(req.session_id)
    try:
        refined = claude_service.refine(req.session_id, req.feedback)
    except LoopLimitError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ClaudeAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return RefineResponse(session_id=req.session_id, refined_title=refined)
