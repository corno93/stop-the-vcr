from __future__ import annotations

from typing import MutableMapping

import vcr
from vcr.matchers import _get_transformer
from vcr.matchers import read_body

__all__ = ["body_structure", "body_types", "body_structure_and_types"]


def body_structure(r1: vcr.request.Request, r2: vcr.request.Request) -> None:
    """Assert that the actual request has the same body structure as the expected
    request in the cassette. Do this by converting both vcr.request.Requests into
    a flat dict and checking that the keys are equal.

    :param r1: The actual request
    :param r2: The expected request found in the cassette
    :returns: None
    :raises AssertionError: if the request bodies do not have the same structure"""
    r1_flat, r2_flat = _prepare_data(r1, r2)
    _assert_body_structure(r1_flat, r2_flat)


def body_types(r1: vcr.request.Request, r2: vcr.request.Request) -> None:
    """Assert that the actual request has the same body field types as the
    expected request in the cassette. Do this by converting both vcr.request.Requests
    into a flat dict and get the types of the body fields. Then check the types are
    equal.

    :param r1: The actual request
    :param r2: The expected request found in the cassette
    :returns: None
    :raises AssertionError: if the request bodies do not have the field types"""
    r1_flat, r2_flat = _prepare_data(r1, r2)
    _assert_body_types(r1_flat, r2_flat)


def body_structure_and_types(r1: vcr.request.Request, r2: vcr.request.Request) -> None:
    """Assert that the actual request has the same body structure and field types as the
    expected request in the cassette. Do this by converting both vcr.request.Requests
    into a flat dict and get the types of the body fields. Then check the keys and
    types are equal.

    :param r1: The actual request
    :param r2: The expected request found in the cassette
    :returns: None
    :raises AssertionError: if the request bodies do not have the same structure
    and field types"""
    r1_flat, r2_flat = _prepare_data(r1, r2)
    _assert_body_structure(r1_flat, r2_flat)
    _assert_body_types(r1_flat, r2_flat)


def _flatten_and_store_value_type(data: dict, parent_key: bool = False) -> dict:
    """Flatten and replace each field's value with the value's type"""
    flat_data = []
    for key, value in data.items():
        new_key = f"{parent_key}_{key}" if parent_key else key
        if isinstance(value, MutableMapping):
            flat_data.extend(_flatten_and_store_value_type(value, new_key).items())
        elif isinstance(value, list):
            for k, v in enumerate(value):
                flat_data.extend(
                    _flatten_and_store_value_type({str(k): v}, new_key).items()
                )
        else:
            flat_data.append((new_key, type(value)))
    return dict(flat_data)


def _prepare_data(
    r1: vcr.request.Request, r2: vcr.request.Request
) -> tuple[dict, dict]:
    """Helper that converts both request's from vcr.request.Request to a flattened
    dict"""
    r1_flat = _get_flat_request_dict(r1)
    r2_flat = _get_flat_request_dict(r2)
    return r1_flat, r2_flat


def _get_flat_request_dict(request: vcr.request.Request) -> dict:
    transformer = _get_transformer(request)
    request_dict = transformer(read_body(request))
    flat_request_dict = _flatten_and_store_value_type(request_dict)
    return flat_request_dict


def _assert_body_structure(r1_flat: dict, r2_flat: dict) -> None:
    assert (
        r1_flat.keys() == r2_flat.keys()
    ), "Difference between actual and expected request structure: {}".format(
        set(r1_flat.keys()).difference(set(r2_flat.keys()))
    )


def _friendly_body_types_assertion_message(r1_flat: dict, r2_flat: dict) -> dict:
    field_errors = {}
    for key, actual_type in r1_flat.items():
        try:
            expected_type = r2_flat[key]
        except KeyError:
            pass
        else:
            if actual_type != expected_type:
                field_errors[
                    key
                ] = f"Actual type: {actual_type} & expected type: {expected_type}"
    return field_errors


def _assert_body_types(r1_flat: dict, r2_flat: dict) -> None:
    common_keys = r1_flat.keys() & r2_flat.keys()
    actual_common_values = {r1_flat[i] for i in common_keys}
    expected_common_values = {r2_flat[i] for i in common_keys}

    assert (
        actual_common_values == expected_common_values
    ), "Difference between actual and expected request field types: {}".format(
        _friendly_body_types_assertion_message(r1_flat, r2_flat)
    )
