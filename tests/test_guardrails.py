"""Unit tests for guardrail functions."""
import pytest
from trip_planner.guardrails.input_guard import validate_input
from trip_planner.guardrails.output_guard import validate_output
from trip_planner.guardrails.content_policy import is_allowed


def test_validate_input_strips_whitespace():
    assert validate_input("  Trip to Bali  ") == "Trip to Bali"


def test_validate_input_raises_on_empty():
    with pytest.raises(ValueError):
        validate_input("")


def test_validate_input_raises_on_short_query():
    with pytest.raises(ValueError):
        validate_input("hi")


def test_validate_output_raises_on_empty():
    with pytest.raises(ValueError):
        validate_output("")


def test_content_policy_allows_normal_destination():
    assert is_allowed("Paris") is True
