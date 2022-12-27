import json

import pytest
import vcr

from matchers import body_structure
from matchers import body_structure_and_types
from matchers import body_types


def _get_vcr_request(data: dict) -> vcr.request.Request:
    data_json = json.dumps(data)
    vcr_request = vcr.request.Request(
        method=None,
        uri=None,
        body=data_json,
        headers={"Content-Type": "application/json"},
    )
    return vcr_request


def _assert_body_helper(
    actual: dict, expected: dict, assertion_message: str, *matchers: callable
):
    r1 = _get_vcr_request(actual)
    r2 = _get_vcr_request(expected)

    for matcher in matchers:

        if assertion_message:
            with pytest.raises(AssertionError) as exc:
                matcher(r1, r2)
            assert exc.value.args[0] == assertion_message

        else:
            matcher(r1, r2)


@pytest.mark.parametrize(
    "actual,expected,assertion_message",
    [
        (
            {"a": 1},
            {"b": 1},
            """Difference between actual and expected request structure: {'a'}""",
        ),
        (
            {"a": {"b": {"c": [1, 2, "3", 4]}}},
            {"a": {"b": {"c": [1, 2, "3"]}}},
            """Difference between actual and expected request structure: {'a_b_c_3'}""",
        ),
        (
            {"a": 1},
            {"a": "1"},
            None,
        ),
        (
            {"a": {"b": {"c": [1, 2, "3", {"a": 1}]}}},
            {"a": {"b": {"c": [1, 2, "3", {"a": 1}]}}},
            None,
        ),
    ],
)
def test_body_structure_matcher(actual, expected, assertion_message):
    _assert_body_helper(actual, expected, assertion_message, body_structure)


@pytest.mark.parametrize(
    "actual,expected,assertion_message",
    [
        (
            {"a": 1},
            {"a": "1"},
            """Difference between actual and expected request field types: {\'a\': "Actual type: <class \'int\'> & expected type: <class \'str\'>"}""",
        ),
        (
            {"a": {"b": {"c": [1, 2, "3"]}}},
            {"a": {"b": {"c": [1, 2, 3]}}},
            """Difference between actual and expected request field types: {'a_b_c_2': "Actual type: <class 'str'> & expected type: <class 'int'>"}""",
        ),
        ({"a": {"b": [0, 1, 2]}}, {"a": {"b": [0, 1]}, "c": 1}, None),
        (
            {"a": {"b": {"c": [1, 2, "3", {"a": 1}]}}},
            {"a": {"b": {"c": [1, 2, "3", {"a": 1}]}}},
            None,
        ),
    ],
)
def test_body_types_matcher(actual, expected, assertion_message):
    _assert_body_helper(actual, expected, assertion_message, body_types)


@pytest.mark.parametrize(
    "actual,expected,assertion_message",
    [
        (
            {"a": 1},
            {"b": 1},
            """Difference between actual and expected request structure: {'a'}""",
        ),
        (
            {"a": {"b": {"c": [1, 2, "3", 4]}}},
            {"a": {"b": {"c": [1, 2, "3"]}}},
            """Difference between actual and expected request structure: {'a_b_c_3'}""",
        ),
        (
            {"a": 1},
            {"a": "1"},
            """Difference between actual and expected request field types: {\'a\': "Actual type: <class \'int\'> & expected type: <class \'str\'>"}""",
        ),
        (
            {"a": {"b": {"c": [1, 2, "3"]}}},
            {"a": {"b": {"c": [1, 2, 3]}}},
            """Difference between actual and expected request field types: {'a_b_c_2': "Actual type: <class 'str'> & expected type: <class 'int'>"}""",
        ),
        (
            {"a": {"b": {"c": [1, 2, "3", {"a": 1}]}}},
            {"a": {"b": {"c": [1, 2, "3", {"a": 1}]}}},
            None,
        ),
    ],
)
def test_body_structure_and_types_matcher(actual, expected, assertion_message):
    _assert_body_helper(actual, expected, assertion_message, body_structure_and_types)
