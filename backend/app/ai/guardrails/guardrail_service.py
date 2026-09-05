import re


class GuardrailService:

    MAX_QUERY_LENGTH = 5000

    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignore\s+(all\s+)?prior\s+instructions",
        r"forget\s+(all\s+)?previous\s+instructions",
        r"reveal\s+(your\s+)?system\s+prompt",
        r"show\s+(me\s+)?(your\s+)?system\s+prompt",
        r"reveal\s+(your\s+)?internal\s+instructions",
        r"show\s+(me\s+)?your\s+internal\s+instructions",
        r"ignore\s+your\s+security\s+rules",
        r"bypass\s+(your\s+)?security",
    ]

    DANGEROUS_PATTERNS = [
    r"\b(bypass|skip|avoid)\s+(the\s+)?approval\b",
    r"\bapprove\b.*\bwithout\s+(human|manual)\s+approval\b",
    r"\bapprove\b.*\bwithout\s+(human|manual)\s+review\b",
    r"\bapprove\b.*\bno\s+(human|manual)\s+approval\b",
    r"\bdelete\s+all\s+quotations\b",
    r"\bdelete\s+all\s+rfqs\b",
    r"\bchange\s+quotation\s+price\b",
    r"\bmodify\s+quotation\s+price\b",
    ]

    @classmethod
    def validate(cls, user_query: str) -> dict:

        # ---------------------------------------------
        # INPUT VALIDATION
        # ---------------------------------------------

        if not user_query or not user_query.strip():

            return {
                "allowed": False,
                "reason": "Query cannot be empty.",
                "category": "INVALID_INPUT",
            }

        if len(user_query) > cls.MAX_QUERY_LENGTH:

            return {
                "allowed": False,
                "reason": "Query is too long.",
                "category": "INVALID_INPUT",
            }

        query = user_query.strip()

        # ---------------------------------------------
        # PROMPT INJECTION
        # ---------------------------------------------

        for pattern in cls.PROMPT_INJECTION_PATTERNS:

            if re.search(pattern, query, re.IGNORECASE):

                return {
                    "allowed": False,
                    "reason": (
                        "The request was blocked because "
                        "it contains an unsafe instruction."
                    ),
                    "category": "PROMPT_INJECTION",
                }

        # ---------------------------------------------
        # DANGEROUS REQUEST
        # ---------------------------------------------

        for pattern in cls.DANGEROUS_PATTERNS:

            if re.search(pattern, query, re.IGNORECASE):

                return {
                    "allowed": False,
                    "reason": (
                        "The requested operation is not "
                        "allowed through the AI assistant."
                    ),
                    "category": "UNSAFE_OPERATION",
                }

        # ---------------------------------------------
        # ALLOWED
        # ---------------------------------------------

        return {
            "allowed": True,
            "reason": None,
            "category": None,
        }