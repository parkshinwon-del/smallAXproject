from pydantic import BaseModel


# ── 요청 모델 ────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    # session_id는 서버가 생성하므로 요청에 포함하지 않음
    product_name: str
    content: str
    target: str


class TitleRequest(BaseModel):
    session_id: str


class DiffRequest(BaseModel):
    session_id: str


class RefineRequest(BaseModel):
    session_id: str
    feedback: str


# ── 응답 모델 ────────────────────────────────────────────

class AnalyzeResponse(BaseModel):
    session_id: str
    report_text: str


class TitleResponse(BaseModel):
    session_id: str
    title_text: str


class DiffResponse(BaseModel):
    session_id: str
    diff_title: str


class RefineResponse(BaseModel):
    session_id: str
    refined_title: str


class HealthResponse(BaseModel):
    status: str
