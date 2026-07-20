import argparse
import sys
import arcade
from src.maze_app.parsing.config_main import load_config
from src.maze_app.output.export import export_to_file
from src.mazegen import MazeGenerator, MazeGenError
from src.maze_app.display.arcade_visualizer import ArcadeVisualizer
from src.maze_app.display.ascii_visualizer import AsciiVisualizer
from debug_utils import print_italic
from src.maze_app.utils.utility_funcs import str_to_bool


def main(config_path: str, cli_vars: dict | None = None) -> None:
    """
    Load and validate maze config
    Initiate, create, validate and solve the maze
    Export maze and solution to a text file
    Display maze

    Exit on failure

    Args:
        config_path (str): Path to the configuration file
        cli_vars (dict | None): Optional values coming from the CLI
            `None` value means "not provided" => NOT override config file.

    Return: None
    """

    # ---------------------------------------------------------------------
    # -------------------- LOAD and VALIDATE maze config ------------------

    # Any CLI vars are passed to `load_config`,
    # to merge them with `config.txt` BEFORE Pydantic validation.
    config = load_config(config_path, cli_vars)

    # ---------------------------------------------------------------------
    # -------------------- GENERATE the maze ------------------------------

    print_italic("\nGenerating the maze...")
    try:
        maze = MazeGenerator(
            width=config.width,
            height=config.height,
            seed=config.seed,
            entry_coord=config.entry_coord,
            exit_coord=config.exit_coord,
            perfect=config.perfect,
        )
        # Initiate, create, validate and solve the maze
        maze.generate()
        print_italic("The generated maze is compliant with mandatory rules.")

    except (ValueError, RuntimeError, MazeGenError) as err:
        print(f"Error during maze processing: {err}", file=sys.stderr)
        sys.exit(1)

    # ---------------------------------------------------------------------
    # --------------- EXPORT maze and solution to a text file -------------

    export_to_file(maze.grid, maze.entry_coord, maze.exit_coord,
                   maze.exit_path, config.output_file)

    # ---------------------------------------------------------------------
    # -------------------- DISPLAY the maze -------------------------------

    if config.display_mode == "ascii":
        visualizer = AsciiVisualizer(maze)
        visualizer.update()
    elif config.display_mode == "arcade":
        window = arcade.Window(1280, 720, "A-Maze-Ing", fullscreen=False)
        visualizer = ArcadeVisualizer(maze)
        window.show_view(visualizer)
        arcade.run()


if __name__ == "__main__":

    # ---------------------------------------------------------------------
    # --------------------- REQUIRED argument -----------------------------

    parser = argparse.ArgumentParser(description="Mazegen execution script")
    parser.add_argument("config_path", type=str,
                        help="Path to the maze configuration file")

    # ---------------------------------------------------------------------
    # --------------------- OPTIONAL arguments ----------------------------

    # default=None if not provided, to prevent overwriting values in config.txt
    parser.add_argument("--seed", type=int, default=None,
                        help="Overrides SEED from the config file")
    parser.add_argument("--display-mode", type=str, default=None,
                        choices=["ascii", "arcade"],
                        help="Overrides DISPLAY_MODE from the config file")
    parser.add_argument("--perfect", type=str_to_bool, default=None,
                        help="Overrides PERFECT from the config file")

    args = parser.parse_args()
    # cli_vars dictionary is constructed using same KEYS as those used later,
    # so that they can be merged directly in config_parsed.
    cli_vars = {
        "SEED": args.seed,
        "DISPLAY_MODE": args.display_mode,
        "PERFECT": args.perfect,
    }

    main(args.config_path, cli_vars)
