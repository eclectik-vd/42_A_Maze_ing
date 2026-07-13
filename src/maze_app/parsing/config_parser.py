from pathlib import Path
from typing import Any


# Pydantic convertit silencieusement MAIS mypy lit le code sans le lancer :
# erreur non gérée par le plugin -> remplacé dict[str, str]: par dict[str, Any]
def parse_config(file_path: str) -> dict[str, Any]:
    """
    Read and extract key-value pairs from a configuration file

    Args:
        file_path (str) : Path to the configuration file

    Returns:
        dict[str, str] : Dictionary containing raw configuration data

    Raises:
        FileNotFoundError: specified config file does not exist
        ValueError: a line (not a comment) does not follows KEY=VALUE format
    """

    # check file exists
    if not Path(file_path).is_file():
        raise FileNotFoundError(f"Error: '{file_path}' file does not exist.")

    config_parsed: dict[str, Any] = {}

    # context manager `with`: to close the file automatically
    with open(file_path, 'r', encoding='utf-8') as config_file:
        for line in config_file:
            # Remove spaces and line breaks around the text
            line = line.strip()

            # Ignore blank lines and comments
            if not line or line.startswith('#'):
                # loop directly to next line
                continue

            # Check for `=` sign in the line
            if '=' not in line:
                raise ValueError(f"'{line}' does not comply KEY=VALUE format")

            # Separate key and value with string.split(separator, maxsplit)
            key, value = line.split('=', 1)
            config_parsed[key.strip().upper()] = value.strip()

    return config_parsed
