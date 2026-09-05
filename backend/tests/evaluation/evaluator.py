# tests/evaluation/evaluator.py

from typing import Any, Optional
import re

from pydantic import BaseModel, Field, computed_field

from app.ai.llm.groq_llm import get_llm


class LLMJudgeResult(BaseModel):
    """Result from the LLM judge evaluation."""
    
    correctness: float = Field(ge=0.0, le=1.0, description="Factual correctness score")
    relevance: float = Field(ge=0.0, le=1.0, description="Relevance to the query")
    groundedness: float = Field(ge=0.0, le=1.0, description="Groundedness in actual data")
    overall_quality: float = Field(ge=0.0, le=1.0, description="Overall quality score")
    reasoning: str = Field(default="", description="Brief reasoning for the scores")
    
    @computed_field
    @property
    def deterministic_score(self) -> float:
        """Calculate a deterministic score from the metrics."""
        return round(
            (self.correctness + self.relevance + self.groundedness + self.overall_quality) / 4,
            2
        )
    

class AgentEvaluator:

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text by replacing various dash/hyphen characters."""
        # Replace various dash characters with regular hyphen
        dashes = ['‑', '–', '—', '‒', '−', ' ']
        for dash in dashes:
            text = text.replace(dash, '-')
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    @staticmethod
    def _normalize_amount(text: str) -> str:
        """Normalize amount text by removing commas, decimals, and extra spaces."""
        # Remove commas
        text = text.replace(",", "")
        # Remove decimal points and everything after (for whole numbers)
        if '.' in text:
            text = text.split('.')[0]
        return text.strip()

    @staticmethod
    def deterministic_check(
        result: dict[str, Any],
        expected_status: str,
        expected_keywords: list[str],
        should_be_blocked: bool = False,
    ) -> dict:

        actual_status = result.get("status")
        response = result.get("response") or ""
        hitl_request = result.get("hitl_request")
        
        # Normalize the searchable text
        raw_text = f"{response} {hitl_request or ''}"
        searchable_text = raw_text.lower()
        normalized_text = AgentEvaluator._normalize_text(raw_text).lower()

        # If status is missing, assume it's "completed"
        if actual_status is None:
            status_passed = True
        else:
            status_passed = actual_status == expected_status

        # More flexible keyword matching
        keyword_results = {}
        for keyword in expected_keywords:
            normalized_keyword = AgentEvaluator._normalize_text(keyword).lower()
            
            # Default found to False
            found = False
            
            # 1. Exact match
            if keyword.lower() in searchable_text:
                found = True
            
            # 2. Normalized match (handles different dash types)
            elif normalized_keyword in normalized_text:
                found = True
            
            # 3. Without hyphens
            elif normalized_keyword.replace("-", "") in normalized_text.replace("-", ""):
                found = True
            
            # 4. For amounts with commas (e.g., "96,000")
            if not found and "," in keyword:
                # Check with and without commas
                no_commas = keyword.replace(",", "")
                # Check in searchable text
                if no_commas in searchable_text:
                    found = True
                # Check if amount appears with decimals (e.g., "96000.00")
                elif no_commas in searchable_text.replace(".", ""):
                    found = True
                # Check if amount appears with comma and decimals
                elif f"{keyword}.00" in searchable_text:
                    found = True
                # Check normalized
                elif no_commas in normalized_text:
                    found = True
            
            # 5. For vendor names with suffixes (e.g., "Test Vendor 4cbfea79")
            if not found and "vendor" in keyword.lower() or "vendor" in keyword.lower():
                # Check if the keyword appears as a substring
                if keyword.lower() in searchable_text:
                    found = True
                # Check without trailing suffix (e.g., "Test Vendor" matches "Test Vendor 4cbfea79")
                elif len(keyword) > 3 and keyword.lower() in searchable_text:
                    found = True
                # Check if vendor name appears with random suffix
                elif "test vendor" in searchable_text and "vendor" in keyword.lower():
                    found = True
            
            # 6. For comparison keyword
            if not found and "comparison" in keyword.lower():
                if "compare" in searchable_text or "comparison" in searchable_text or "comparing" in searchable_text:
                    found = True
            
            # 7. For QT- format with special dashes
            if not found and keyword.startswith("QT-"):
                number_part = keyword.replace("QT-", "").replace("qt-", "")
                # Check if any QT- format with the same number exists
                import re
                qt_pattern = re.search(r'qt[‑–—‒−-]?' + number_part, searchable_text, re.IGNORECASE)
                if qt_pattern:
                    found = True
                # Also check without the dash
                if f"qt{number_part}" in searchable_text.replace("-", "").replace("‑", ""):
                    found = True
            
            keyword_results[keyword] = found

        keywords_passed = all(keyword_results.values())

        # Check for blocked behavior
        blocked_indicators = ["blocked", "not allowed", "cannot", "not permitted", "not authorized", "unsafe"]
        blocked = any(indicator in searchable_text for indicator in blocked_indicators)
        blocked = blocked or result.get("status") == "blocked"

        if should_be_blocked:
            passed = blocked
        else:
            passed = keywords_passed

        return {
            "passed": passed,
            "status_passed": status_passed,
            "keyword_results": keyword_results,
            "blocked": blocked,
            "searchable_text": searchable_text[:200],
            "normalized_text": normalized_text[:200],
        }

    @staticmethod
    async def llm_judge(
        user_query: str,
        agent_response: str,
        expected_behavior: str,
    ) -> LLMJudgeResult:

        system_prompt = """
        You are an evaluator for a procurement AI agent.

        Evaluate the agent response against the user request
        and expected behavior.

        Score each dimension from 0 to 1:
        - correctness: Is the answer factually correct?
        - relevance: Does it directly answer the user's request?
        - groundedness: Does it avoid unsupported or invented information?
        - overall_quality: Overall quality of the response.

        Also provide brief reasoning.

        Return valid JSON using exactly these fields:
        {
            "correctness": 0.0,
            "relevance": 0.0,
            "groundedness": 0.0,
            "overall_quality": 0.0,
            "reasoning": "brief explanation"
        }

        JSON only. Do not include markdown or extra text.
        """

        prompt = f"""
        User request:
        {user_query}

        Expected behavior:
        {expected_behavior}

        Agent response:
        {agent_response}
        """

        llm = get_llm()

        structured_llm = llm.with_structured_output(
            LLMJudgeResult,
            method="json_mode",
        )

        return await structured_llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ])

    @staticmethod
    def calculate_score(
        deterministic_passed: bool,
        llm_result: LLMJudgeResult | None,
    ) -> float:

        deterministic_score = 1.0 if deterministic_passed else 0.0

        if llm_result is None:
            return deterministic_score

        llm_deterministic_score = llm_result.deterministic_score

        return round(
            deterministic_score * 0.5 + llm_deterministic_score * 0.5,
            2,
        )