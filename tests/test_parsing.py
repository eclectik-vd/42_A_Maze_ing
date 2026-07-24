from pathlib import Path
import pytest

from src.maze_app.parsing.config_parser import parse_config


def test_file_not_found(tmp_path: Path) -> None:
    """Verify that parsing a non-existent file raises ``FileNotFoundError``.

    Args:
        tmp_path (Path): Pytest-provided temporary directory used to
            build a path to a config file that is never created.

    Returns:
        None
    """

    config_file = tmp_path / "config.txt"

    with pytest.raises(FileNotFoundError):
        parse_config(str(config_file))


def test_line_without_equals_sign(tmp_path: Path) -> None:
    """Verify that a line without an ``=`` sign raises ``ValueError``.

    Args:
        tmp_path (Path): Pytest-provided temporary directory used to
            create the malformed config file.

    Returns:
        None
    """

    config_file = tmp_path / "config.txt"
    config_file.write_text("a line without the equals sign\n")

    with pytest.raises(ValueError):
        parse_config(str(config_file))


def test_line_without_equals_sign_v2(tmp_path: Path) -> None:
    """Verify that the ``ValueError`` for a missing ``=``\
      has the expected message.

    Args:
        tmp_path (Path): Pytest-provided temporary directory used to
            create the malformed config file.

    Returns:
        None
    """

    config_file = tmp_path / "config.txt"
    config_file.write_text("a line without the equals sign\n")

    with pytest.raises(ValueError, match="does not comply KEY=VALUE format"):
        parse_config(str(config_file))


def test_empty_file(tmp_path: Path) -> None:
    """Verify that parsing an empty file returns an empty dictionary.

    Args:
        tmp_path (Path): Pytest-provided temporary directory used to
            create the empty config file.

    Returns:
        None
    """

    config_file = tmp_path / "config.txt"
    config_file.write_text("")

    assert parse_config(str(config_file)) == {}


def test_file_comments(tmp_path: Path) -> None:
    """Verify that a file containing only comments returns an empty dictionary.

    Args:
        tmp_path (Path): Pytest-provided temporary directory used to
            create the comment-only config file.

    Returns:
        None
    """

    config_file = tmp_path / "config.txt"
    config_file.write_text("# only comments")

    assert parse_config(str(config_file)) == {}


def test_file_empty_lines(tmp_path: Path) -> None:
    """Verify that a file with only a comment and blank lines\
      returns an empty dictionary.

    Args:
        tmp_path (Path): Pytest-provided temporary directory used to
            create the config file with blank lines.

    Returns:
        None
    """

    config_file = tmp_path / "config.txt"
    config_file.write_text("#\n\n")

    assert parse_config(str(config_file)) == {}
