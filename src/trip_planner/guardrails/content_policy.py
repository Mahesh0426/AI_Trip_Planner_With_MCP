"""Content Policy
Defines rules about what the trip planner will and won't handle.
"""

# Destinations that require special handling or are restricted
RESTRICTED_DESTINATIONS: set[str] = set()

# Maximum allowed budget (USD) — adjust as needed
MAX_BUDGET_USD = 1_000_000


def is_allowed(destination: str, budget: float | None = None) -> bool:
    """
    Check whether a trip request passes content policy.
    Returns True if allowed, False if restricted.
    
    TODO: Expand with sanctions list, safe-travel advisories, etc.
    """
    if destination.lower() in {d.lower() for d in RESTRICTED_DESTINATIONS}:
        return False

    if budget is not None and budget > MAX_BUDGET_USD:
        return False

    return True
