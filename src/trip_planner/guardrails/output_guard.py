"""Output Guardrail
Validates the final LLM response before it is shown to the user.

Checks performed
----------------
1. Empty / whitespace-only response — the LLM returned nothing useful.
2. Refusal detection — the LLM said it can't help (e.g. "I'm sorry, I can't…").
3. Minimum length — a real travel plan can't be 10 words long.
4. Travel-content sanity — the response should mention at least one travel
   keyword (day, hotel, flight, itinerary, etc.) to catch hallucinated
   completely off-topic replies.

On failure the guardrail raises OutputGuardrailError (a ValueError subclass)
so the caller can decide whether to retry, surface the error, or fall back.
"""

from __future__ import annotations


# ──────────────────────────────────────────────────────────────────────────────
# Custom exception
# ──────────────────────────────────────────────────────────────────────────────

class OutputGuardrailError(ValueError):
    """Raised when the output guardrail rejects the LLM response."""


# ──────────────────────────────────────────────────────────────────────────────
# Check helpers
# ──────────────────────────────────────────────────────────────────────────────

# Phrases that signal an LLM refusal
_REFUSAL_PHRASES: tuple[str, ...] = (
    "i'm sorry, i can't",
    "i am sorry, i cannot",
    "i can't help with that",
    "i cannot help with that",
    "i'm unable to",
    "i am unable to",
    "as an ai, i",
    "as an ai language model",
)

# At least one of these must appear in a valid travel plan response
_TRAVEL_KEYWORDS: tuple[str, ...] = (
    "day", "hotel", "flight", "itinerary", "trip", "travel",
    "destination", "accommodation", "airport", "budget", "activity",
    "morning", "evening", "night", "afternoon", "visit", "explore",
)

# A real travel plan must be at least this many characters
_MIN_LENGTH = 100


def _check_empty(response: str) -> None:
    if not response or not response.strip():
        raise OutputGuardrailError("LLM returned an empty response.")


def _check_refusal(response: str) -> None:
    lowered = response.lower()
    for phrase in _REFUSAL_PHRASES:
        if phrase in lowered:
            raise OutputGuardrailError(
                f"LLM refused to answer (detected phrase: '{phrase}')."
            )


def _check_min_length(response: str) -> None:
    if len(response.strip()) < _MIN_LENGTH:
        raise OutputGuardrailError(
            f"Response is too short ({len(response.strip())} chars) "
            f"to be a valid travel plan (minimum {_MIN_LENGTH} chars)."
        )


def _check_travel_content(response: str) -> None:
    lowered = response.lower()
    if not any(kw in lowered for kw in _TRAVEL_KEYWORDS):
        raise OutputGuardrailError(
            "Response does not appear to contain travel-related content."
        )


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def validate_output(response: str) -> str:
    """
    Validate the LLM's final travel plan response.

    Runs four checks in order:
      1. Not empty
      2. Not a refusal
      3. Minimum length (100 chars)
      4. Contains at least one travel keyword

    Parameters
    ----------
    response:
        The raw string returned by the LLM.

    Returns
    -------
    str
        The cleaned (stripped) response if all checks pass.

    Raises
    ------
    OutputGuardrailError
        If any check fails. The caller should catch this and either retry
        or surface a friendly error to the user.
    """
    _check_empty(response)
    _check_refusal(response)
    _check_min_length(response)
    _check_travel_content(response)

    return response.strip()
