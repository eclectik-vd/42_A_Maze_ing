import pytest
from pydantic import ValidationError

from src.maze_app.parsing.models import MazeConfig


# ================== DICTIONNAIRE VALIDE de référence =====================

@pytest.fixture
def a_valid_config():
    return {
        "WIDTH": "100", "HEIGHT": "100",
        "ENTRY": "0,0", "EXIT": "6,10",
        "OUTPUT_FILE": "maze.txt",
    }


# ========================== MISSIMG FIELDS =============================

@pytest.mark.parametrize("missing_field",
                         ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",])
def test_missing_required_field(a_valid_config, missing_field):
    del a_valid_config[missing_field]

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# ========================== VALEURS INVALIDES ============================

# -------------------- TEST WIDTH / HEIGHT invalides ----------------------

@pytest.mark.parametrize("a_field, invalid_value", [
    ("WIDTH", "NOT AN INT"),
    ("WIDTH", "1"),      # off the map : < 2
    ("WIDTH", "201"),    # off the map : > 200
    ("HEIGHT", "NOT AN INT"),
    ("HEIGHT", "1"),
    ("HEIGHT", "201"),
])
def test_invalid_width_height(a_valid_config, a_field, invalid_value):
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
def test_entry_exit_invalides(a_valid_config, a_field, invalid_value):
    a_valid_config[a_field] = invalid_value

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# ----------- TEST file extension NOT `.txt` in OUTPUT_FILE ---------------

def test_output_ext_not_txt(a_valid_config):
    a_valid_config["OUTPUT_FILE"] = "txt.maze"

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# ----------- TEST DISPLAY_MODE not in {ascii, arcade} --------------

def test_display_mode_unknown(a_valid_config):
    a_valid_config["DISPLAY_MODE"] = "somethingElse"

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# -------------- TEST PERFECT non convertible en booléen ------------------

def test_perfect_not_bool(a_valid_config):
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
def test_bad_business_rule(a_valid_config, a_field, invalid_value):
    a_valid_config[a_field] = invalid_value

    with pytest.raises(ValidationError):
        MazeConfig(**a_valid_config)


# -------------------------- many business rules ------------------------

@pytest.mark.parametrize("field1, value1, field2, value2, expected_words", [
    ("ENTRY", "101,0", "EXIT", "101,0",
     ["entry abcisse", "exit abcisse", "must be different"]),
    ("ENTRY", "101,200", "EXIT", "200,101",
     ["entry abcisse", "entry ordinate", "exit abcisse", "exit ordinate"]),
])
def test_many_rules(a_valid_config, field1, value1, field2, value2,
                    expected_words):
    a_valid_config[field1] = value1
    a_valid_config[field2] = value2

    with pytest.raises(ValidationError) as exception_msg:
        MazeConfig(**a_valid_config)

    message = str(exception_msg.value)
    for a_word in expected_words:
        assert a_word in message
