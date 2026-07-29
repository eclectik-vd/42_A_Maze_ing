import mazegen
import sys


def print_italic(msg: str) -> None:
    """Print the output in italic"""
    print(f"\033[3m{msg}\033[0m")


def main() -> None:
    print_italic("\nGenerating the maze...")
    try:
        maze = mazegen.MazeGenerator(
            width=10,
            height=10,
            seed=42,
            entry_coord=tuple((2, 9)),
            exit_coord=tuple((6, 2)),
            perfect=False,
            output_file="output.txt",
        )
        # Initiate, create, validate, solve and export the maze
        maze.generate()
        print_italic("The generated maze is compliant with mandatory rules.")

        for line in maze.grid:
            print(line)
        print()

    except (ValueError, RuntimeError) as err:
        print(f"Error during maze processing: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
