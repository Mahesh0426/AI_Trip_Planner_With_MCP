"""Input Guardrail
Validates and sanitises the user query before it enters the graph.
Raises ValueError for off-topic or unsafe inputs.
"""


def validate_input(user_query: str) -> str:
    """
    Validate the user's travel request.
    - Strips leading/trailing whitespace.
    - Raises ValueError if the query is empty or off-topic.
    
    TODO: Add LLM-based relevance check and PII scrubbing.
    """
    query = user_query.strip()

    if not query:
        raise ValueError("User query cannot be empty.")

    if len(query) < 10:
        raise ValueError("Query is too short to be a valid travel request.")

    # TODO: Add off-topic detection (e.g. "order pizza", "write code")
    # TODO: Add PII scrubbing (phone numbers, credit cards)

    return query
