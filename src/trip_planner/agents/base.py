import json

from langchain_core.messages import HumanMessage, SystemMessage

from ..config import get_llm
from ..schemas import SupervisorDecision

# Shared LLM instance
llm = get_llm()

# Structured LLM with supervisor decision schema
structured_llm = llm.with_structured_output(SupervisorDecision)

# A helper function to call LLM with system prompt and return plain text response.
def _llm_text(system: str, prompt: str) -> str:
    """Call the LLM and return plain text response."""
    response = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=prompt),
        ]
    )
    return response.content


# A utility function to parse JSON string output from LLM into Python dict.
def _json_from_llm(text: str) -> dict:
    """Convert raw LLM text response to a Python dict by extracting JSON."""
    print("\n========== RAW LLM RESPONSE ==========")
    print(text)
    print("======================================\n")

    # Search the first '{' and last '}' and extract the JSON
    start = text.index("{")
    end = text.rindex("}") + 1
    json_text = text[start:end]

    print("\n========== EXTRACTED JSON ==========")
    print(json_text)
    print("====================================\n")

    return json.loads(json_text)
