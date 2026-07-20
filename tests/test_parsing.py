import pytest

from src.maze_app.parsing.config_parser import parse_config


def test_file_not_found(tmp_path):
    config_file = tmp_path / "config.txt"

    with pytest.raises(FileNotFoundError):
        parse_config(str(config_file))


def test_line_without_equals_sign(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text("a line without the equals sign\n")

    with pytest.raises(ValueError):
        parse_config(str(config_file))


def test_line_without_equals_sign_v2(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text("a line without the equals sign\n")

    with pytest.raises(ValueError, match="does not comply KEY=VALUE format"):
        parse_config(str(config_file))


def test_empty_file(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text("")

    assert parse_config(str(config_file)) == {}


def test_file_comments(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text("# only comments")

    assert parse_config(str(config_file)) == {}


def test_file_empty_lines(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text("#\n\n")

    assert parse_config(str(config_file)) == {}
