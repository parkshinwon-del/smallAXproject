class PromptService:
    TITLE_RULES: str = (
        "핵심 상품명이 제목 맨 앞쪽에 나올수록 좋다. 제목은 15글자 미만으로 쓰기. "
        "타겟의 특성이 일치하는 SNS 유행 콘텐츠의 어조 쓰기."
    )

    DIFFERENTIATE_PROMPT: str = (
        "위 제목을 차별화해줘. "
        "기준은 네이버 상위노출 페이지에 나오는 콘텐츠 제목과 달라야 돼."
    )

    @staticmethod
    def build_analyze_prompt(product_name: str, content: str, target: str) -> str:
        return (
            f"상품명: {product_name}\n"
            f"콘텐츠: {content}\n"
            f"타겟: {target}\n\n"
            "위 정보를 바탕으로 마케팅 타겟 분석 보고서를 요약해줘."
        )

    @staticmethod
    def build_title_prompt() -> str:
        return (
            "위 분석 결과를 바탕으로 마케팅 제목을 만들어줘.\n"
            f"{PromptService.TITLE_RULES}"
        )

    @staticmethod
    def build_differentiate_prompt() -> str:
        return PromptService.DIFFERENTIATE_PROMPT

    @staticmethod
    def build_refine_prompt(feedback: str) -> str:
        return f"피드백: {feedback}\n위 피드백을 반영해서 제목을 다시 만들어줘."
