"""Output Guardrail
Validates the final LLM response before it is shown to the user.
"""


def validate_output(response: str) -> str:
    """
    Validate the LLM's final response.
    - Checks response is not empty or a refusal.
    
    TODO: Add toxicity check, hallucination detection.
    """
    if not response or not response.strip():
        raise ValueError("LLM returned an empty response.")

    # TODO: Add toxicity / harmful content check
    # TODO: Flag if response contains unsupported claims

    return response.strip()
