def print_italic(msg: str) -> None:
    print(f"\033[3m{msg}\033[0m")


def print_green(msg: str, end_msg: str = '\n') -> None:
    print(f"\033[32m{msg}\033[0m", end=end_msg)


def print_red(msg: str) -> None:
    print(f"\033[31m{msg}\033[0m")


def debug_draw_maze(grid: list[list[int]], width: int, height: int) -> None:
    """
    draw generated (empty) maze in ASCII
    """

    dir_S: int = 4
    dir_W: int = 8

    # upper edge of the labyrinth
    for _ in range(width):
        print_green("+---", "")
    print_green("+")

    for y in range(height):

        # corridor with west walls
        for x in range(width):
            if grid[y][x] & dir_W:
                print_green("|   ", "")
            else:
                print_green("    ", "")
        # end of the corridor
        print_green("|")

        # floor with south walls
        for x in range(width):
            if grid[y][x] & dir_S:
                print_green("+---", "")
            else:
                print_green("+   ", "")
        # end of the floor
        print_green("+")
