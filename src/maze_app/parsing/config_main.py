import sys
from pydantic import ValidationError
from src.maze_app.parsing.config_parser import parse_config
from src.maze_app.parsing.models import MazeConfig
from src.maze_app.utils.utility_funcs import print_italic, print_green


def load_config(config_path: str, cli_vars: dict | None = None) -> MazeConfig:
    """
    Load, parse, and validate maze configuration.
    Exit on failure

    Args:
        config_path (str): Path to the configuration file
        cli_vars (dict | None): Optional values coming from the CLI
            `None` value means "not provided" => NOT override config file.

    Return: MazeConfig
    """

    # ---------------------------------------------------------------------
    # --------- EXTRACT configuration from the `config_path` file ---------

    print_italic(f"\nReading the configuration file: {config_path}")
    try:
        config_parsed = parse_config(config_path)

    except (FileNotFoundError, PermissionError) as err:
        print(f"Error: the file '{config_path}' can't be accessed\n {err}",
              file=sys.stderr)
        sys.exit(1)
    except ValueError as err:
        print(f"Error: bad syntax in the configuration file: {err}",
              file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"Unexpected error during parsing: {err}", file=sys.stderr)
        sys.exit(1)

    # ---------------------------------------------------------------------
    # ---------------- if provided, OVERRIDE with cli_vars ----------------

    # make Mypy happy
    if cli_vars is None:
        print_italic("No value passed via CLI to apply to config_parsed")

    else:
        cli_values = set(value for value in cli_vars.values())
        if len(cli_values) == 1 and None in cli_values:
            print_italic("No valid CLI value to apply to config_parsed")

        else:
            print_italic("Apply to config_parsed any value passed via the CLI")
            for key, value in cli_vars.items():
                if value is not None:
                    print_green(f"  '{key}' overridden by CLI: '{value}'")
                    config_parsed[key] = value

    # ---------------------------------------------------------------------
    # ------------- VALIDATE config and data model with Pydantic ----------

    print_italic("Validating data configuration")
    try:
        config = MazeConfig(**config_parsed)

    except ValidationError as err:
        print("Error validating maze parameters:", file=sys.stderr)
        for error in err.errors():
            loc = error.get('loc', ())
            field_name = loc[0] if loc else "Global"
            raw_msg = error.get('msg', '')
            cleaned_msg = raw_msg.replace('Value error,', '').strip()
            print(f"  - [{field_name}] : {cleaned_msg}", file=sys.stderr)
        sys.exit(1)

    print_italic("Config successfully validated! ")
    return config
