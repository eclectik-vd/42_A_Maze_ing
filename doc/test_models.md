from typing import Any

import pytest
from pydantic import ValidationError

from src.maze_app.parsing.models import MazeConfig


# ================== DICTIONNAIRE VALIDE de référence =====================

@pytest.fixture
def a_valid_config() -> dict[str, Any]:
    """Provide a minimal, valid maze configuration dictionary.

    Returns:
        dict[str, Any]: A dictionary containing all required
        ``MazeConfig`` fields (``WIDTH``, ``HEIGHT``, ``ENTRY``,
        ``EXIT``, ``OUTPUT_FILE``) with values that pass validation.
        Individual tests mutate a copy of this fixture to introduce
        specific invalid values.
    """
    return {
        "WIDTH": "100", "HEIGHT": "100",
        "ENTRY": "0,0", "EXIT": "6,10",
        "OUTPUT_FILE": "maze.txt",
    }


# ========================== MISSIMG FIELDS =============================

@pytest.mark.parametrize("missing_field",
                         ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",])
def test_missing_required_field(a_valid_config: dict[str, Any],
                                missing_field: str) -> None:
    """Verify that omitting any required field raises a ``ValidationError``.

    Args:
        a_valid_config (dict[str, Any]): A valid base configuration,
            supplied by the ``a_valid_config`` fixture.
        missing_field (str): The name of the required field to remove
            from the configuration before validation.

    Returns:
        None
    """
    del a_valid_config[missing_field]

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# ========================== VALEURS INVALIDES ============================

# -------------------- TEST WIDTH / HEIGHT invalides ----------------------

@pytest.mark.parametrize("a_field, invalid_value", [
    ("WIDTH", "NOT AN INT"),
    ("WIDTH", "1"),      # off the map : < 2
    ("WIDTH", "101"),    # off the map : > 100
    ("HEIGHT", "NOT AN INT"),
    ("HEIGHT", "1"),
    ("HEIGHT", "201"),
])
def test_invalid_width_height(a_valid_config: dict[str, Any], a_field: str,
                              invalid_value: str) -> None:
    """Verify that out-of-range or non-numeric WIDTH/HEIGHT values fail.

    Args:
        a_valid_config (dict[str, Any]): A valid base configuration,
            supplied by the ``a_valid_config`` fixture.
        a_field (str): The field under test, either ``"WIDTH"`` or
            ``"HEIGHT"``.
        invalid_value (str): The invalid value to assign to ``a_field``
            (e.g. non-numeric text, or a value outside the allowed
            bounds).

    Returns:
        None
    """
    a_valid_config[a_field] = invalid_value

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# -------------------- TEST invalid ENTRY / EXIT -------------------------

@pytest.mark.parametrize("a_field, invalid_value", [
    ("ENTRY", "22"),      # incorrect format: no comma
    ("ENTRY", "a,2"),     # non-integer coordinate
    ("ENTRY", "-2,2"),    # negative coordinate
    ("EXIT", "33"),
    ("EXIT", "1,b"),
    ("EXIT", "1,-1"),
])
def test_entry_exit_invalides(a_valid_config: dict[str, Any], a_field: str,
                              invalid_value: str) -> None:
    """Verify that malformed ENTRY/EXIT coordinate strings fail validation.

    Covers missing comma separators, non-integer coordinate components,
    and negative coordinate values.

    Args:
        a_valid_config (dict[str, Any]): A valid base configuration,
            supplied by the ``a_valid_config`` fixture.
        a_field (str): The field under test, either ``"ENTRY"`` or
            ``"EXIT"``.
        invalid_value (str): The malformed coordinate string to assign
            to ``a_field``.

    Returns:
        None
    """
    a_valid_config[a_field] = invalid_value

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# ----------- TEST file extension NOT `.txt` in OUTPUT_FILE ---------------

def test_output_ext_not_txt(a_valid_config: dict[str, Any]) -> None:
    """Verify that an ``OUTPUT_FILE`` lacking a ``.txt`` extension fails.

    Args:
        a_valid_config (dict[str, Any]): A valid base configuration,
            supplied by the ``a_valid_config`` fixture.

    Returns:
        None
    """
    a_valid_config["OUTPUT_FILE"] = "txt.maze"

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# ----------- TEST DISPLAY_MODE not in {ascii, arcade} --------------

def test_display_mode_unknown(a_valid_config: dict[str, Any]) -> None:
    """Verify that an unrecognized ``DISPLAY_MODE`` value fails validation.

    Args:
        a_valid_config (dict[str, Any]): A valid base configuration,
            supplied by the ``a_valid_config`` fixture.

    Returns:
        None
    """
    a_valid_config["DISPLAY_MODE"] = "somethingElse"

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# -------------- TEST PERFECT non convertible en booléen ------------------

def test_perfect_not_bool(a_valid_config: dict[str, Any]) -> None:
    """Verify that a non-boolean-convertible ``PERFECT`` value fails.

    Args:
        a_valid_config (dict[str, Any]): A valid base configuration,
            supplied by the ``a_valid_config`` fixture.

    Returns:
        None
    """
    a_valid_config["PERFECT"] = "notAbool"

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# ============================ VIOLATED RULES =============================

# -------------------------- each business rules --------------------------
@pytest.mark.parametrize("a_field, invalid_value", [
    ("ENTRY", "101,0"),   # entry_coord.x >= width
    ("ENTRY", "0,101"),   # entry_coord.y >= height
    ("EXIT", "101,0"),    # exit_coord.x >= width
    ("EXIT", "0,101"),    # exit_coord.y >= height
    ("EXIT", "0,0"),      # entry_coord == exit_coord
])
def test_bad_business_rule(a_valid_config: dict[str, Any], a_field: str,
                           invalid_value: str) -> None:
    """Verify that a single business-rule violation raises a validation error.

    Covers coordinates that fall outside the maze bounds (``x`` or ``y``
    greater than or equal to ``WIDTH``/``HEIGHT``) and an ``EXIT`` equal
    to ``ENTRY``.

    Args:
        a_valid_config (dict[str, Any]): A valid base configuration,
            supplied by the ``a_valid_config`` fixture.
        a_field (str): The field under test, either ``"ENTRY"`` or
            ``"EXIT"``.
        invalid_value (str): The coordinate value that violates a
            business rule.

    Returns:
        None
    """
    a_valid_config[a_field] = invalid_value

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# -------------------------- many business rules ------------------------

@pytest.mark.parametrize("field1, value1, field2, value2, expected_words", [
    ("ENTRY", "51,0", "EXIT", "51,0",
     ["entry abcisse", "exit abcisse", "must be different"]),
    ("ENTRY", "51,100", "EXIT", "100,51",
     ["entry abcisse", "entry ordinate", "exit abcisse", "exit ordinate"]),
])
def test_many_rules(a_valid_config: dict[str, Any], field1: str, value1: str,
                    field2: str, value2: str,
                    expected_words: list[str]) -> None:
    """Verify that multiple simultaneous business-rule\
    violations are all reported.

    Sets two fields to values that each violate one or more business
    rules, then asserts that the resulting ``ValidationError`` message
    mentions every expected keyword.

    Args:
        a_valid_config (dict[str, Any]): A valid base configuration,
            supplied by the ``a_valid_config`` fixture.
        field1 (str): The name of the first field to set (``"ENTRY"``
            or ``"EXIT"``).
        value1 (str): The invalid value to assign to ``field1``.
        field2 (str): The name of the second field to set (``"ENTRY"``
            or ``"EXIT"``).
        value2 (str): The invalid value to assign to ``field2``.
        expected_words (list[str]): Substrings expected to appear in
            the raised ``ValidationError``'s message.

    Returns:
        None
    """
    a_valid_config[field1] = value1
    a_valid_config[field2] = value2

    with pytest.raises(ValidationError) as exception_msg:
        MazeConfig(**a_valid_config)

    message = str(exception_msg.value)
    for a_word in expected_words:
        assert a_word in message
