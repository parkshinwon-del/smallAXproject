import pytest
from pydantic import ValidationError


def test_analyze_request_valid():
    from titlegene.models.schemas import AnalyzeRequest
    r = AnalyzeRequest(product_name="무릎보호대", content="글내용", target="50대여성")
    assert r.product_name == "무릎보호대"


def test_analyze_request_missing_fields():
    from titlegene.models.schemas import AnalyzeRequest
    with pytest.raises(ValidationError):
        AnalyzeRequest(product_name="무릎보호대")  # content, target 누락


def test_title_request_valid():
    from titlegene.models.schemas import TitleRequest
    r = TitleRequest(session_id="s1")
    assert r.session_id == "s1"


def test_diff_request_valid():
    from titlegene.models.schemas import DiffRequest
    r = DiffRequest(session_id="s1")
    assert r.session_id == "s1"


def test_refine_request_valid():
    from titlegene.models.schemas import RefineRequest
    r = RefineRequest(session_id="s1", feedback="좀 더 젊게")
    assert r.feedback == "좀 더 젊게"


def test_refine_request_missing_feedback():
    from titlegene.models.schemas import RefineRequest
    with pytest.raises(ValidationError):
        RefineRequest(session_id="s1")  # feedback 필수


def test_analyze_response():
    from titlegene.models.schemas import AnalyzeResponse
    r = AnalyzeResponse(session_id="s1", report_text="보고서")
    assert r.report_text == "보고서"


def test_title_response():
    from titlegene.models.schemas import TitleResponse
    r = TitleResponse(session_id="s1", title_text="무릎보호대 관절 걱정 끝")
    assert r.title_text == "무릎보호대 관절 걱정 끝"


def test_diff_response():
    from titlegene.models.schemas import DiffResponse
    r = DiffResponse(session_id="s1", diff_title="무릎보호대, 엄마 선물로 딱")
    assert r.diff_title == "무릎보호대, 엄마 선물로 딱"


def test_refine_response():
    from titlegene.models.schemas import RefineResponse
    r = RefineResponse(session_id="s1", refined_title="무릎보호대 지금 바로")
    assert r.refined_title == "무릎보호대 지금 바로"
