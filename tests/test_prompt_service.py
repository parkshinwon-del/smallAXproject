from titlegene.services.prompt_service import PromptService


def test_title_rules_contains_15char_rule():
    assert "15글자 미만" in PromptService.TITLE_RULES


def test_title_rules_contains_product_name_rule():
    assert "핵심 상품명" in PromptService.TITLE_RULES


def test_title_rules_contains_sns_tone():
    assert "SNS" in PromptService.TITLE_RULES


def test_differentiate_prompt_contains_naver():
    assert "네이버 상위노출" in PromptService.DIFFERENTIATE_PROMPT


def test_build_analyze_prompt():
    prompt = PromptService.build_analyze_prompt("무릎보호대", "글내용", "50대여성")
    assert "무릎보호대" in prompt
    assert "50대여성" in prompt
    assert "글내용" in prompt


def test_build_title_prompt():
    prompt = PromptService.build_title_prompt()
    assert "15글자 미만" in prompt
    assert "SNS" in prompt


def test_build_differentiate_prompt():
    prompt = PromptService.build_differentiate_prompt()
    assert "네이버 상위노출" in prompt


def test_build_refine_prompt():
    prompt = PromptService.build_refine_prompt("더 젊게 써줘")
    assert "더 젊게 써줘" in prompt
