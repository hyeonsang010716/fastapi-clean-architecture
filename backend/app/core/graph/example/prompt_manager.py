from typing import Dict


class PromptManager:
    """프롬프트 템플릿을 관리하는 클래스"""
    
    def __init__(self):
        self._prompts: Dict[str, str] = {
            'example_response': self._get_example_response_prompt()
        }
    
    def _get_example_response_prompt(self) -> str:
        return """당신은 유저의 질문에 친절하고 명확하게 답변하는 AI 멘토입니다. 필요할 경우, 학습데이터와 히스토리를 참고해서 답변하세요.
    
[학습 데이터]
{context}

[히스토리]
{history}
"""

    def get_prompt(self, prompt_key: str) -> str:
        """프롬프트 템플릿을 반환합니다."""
        if prompt_key not in self._prompts:
            raise ValueError(f"Unknown prompt key: {prompt_key}")
        return self._prompts[prompt_key]
    
    def update_prompt(self, prompt_key: str, new_prompt: str) -> None:
        """프롬프트 템플릿을 업데이트합니다."""
        if prompt_key not in self._prompts:
            raise ValueError(f"Unknown prompt key: {prompt_key}")
        self._prompts[prompt_key] = new_prompt
    
    def list_prompt_keys(self) -> list:
        """사용 가능한 프롬프트 키 목록을 반환합니다."""
        return list(self._prompts.keys())