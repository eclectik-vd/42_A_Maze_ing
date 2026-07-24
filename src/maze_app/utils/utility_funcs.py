import argparse


# en Python toute chaine non vide vaut True
# il faut donc interpréter EXPLICITEMENT l'arg PERFECT passé en CLI
def str_to_bool(value: str) -> bool:
    """
    Convert a CLI string argument to a proper boolean.

    Args:
        value (str): raw string received from argparse (e.g. "True",
            "false", "1", "no", ...)

    Returns:
        bool: the interpreted boolean value

    Raises:
        argparse.ArgumentTypeError: if `value` cant be interpreted as boolean.
    """
    if value.lower() in ("true", "1", "yes"):
        return True
    if value.lower() in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError(
        f"Boolean value expected ('True'/'False'), got '{value}'"
    )


def print_italic(msg: str) -> None:
    """Print the output in italic"""
    print(f"\033[3m{msg}\033[0m")


def print_green(msg: str, end_msg: str = '\n') -> None:
    """Print the output in green"""
    print(f"\033[32m{msg}\033[0m", end=end_msg)
