from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.ai.llm.groq_llm import get_llm
from app.ai.schemas.memory import MemoryExtraction


class MemoryExtractor:

    @staticmethod
    async def extract(
        user_query: str,
        assistant_response: str,
    ) -> MemoryExtraction:

        system_prompt = """
        You are a memory extraction system for a procurement
        AI assistant.

        Your job is to identify information that is genuinely
        useful to remember about the user for future conversations.

        Store information such as:

        - User preferences
        - User's recurring procurement preferences
        - Stable user-provided facts
        - Important recurring requirements

        Do NOT store:

        - Temporary questions
        - RFQ numbers
        - Vendor IDs
        - Quotation IDs
        - Database information
        - Sensitive credentials
        - Passwords
        - Financial account information
        - Entire conversations
        - Normal one-time requests

        Only create a memory when the information is genuinely
        useful for future conversations.

        If there is nothing worth remembering:

        should_remember = false

        Return the result as valid JSON matching the required schema.
        Return JSON only.
        """

        messages = [
            SystemMessage(content=system_prompt),

            HumanMessage(
                content=f"""
                User message:
                {user_query}

                Assistant response:
                {assistant_response}
                """
            ),
        ]

        llm = get_llm()

        structured_llm = llm.with_structured_output(
            MemoryExtraction,
            method="json_mode",
        )

        return await structured_llm.ainvoke(messages)