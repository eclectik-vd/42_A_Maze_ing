def export_to_file(grid: list[list[int]],
                   entry_coord: tuple[int, int], exit_coord: tuple[int, int],
                   path: str, file_name: str,) -> None:
    """
    Export the maze and its solution to the mandatory text file
    """
    with open(file_name, 'w', encoding='utf-8') as new_file:
        # Write grid in hexa
        for row in grid:
            # f"{integer:X}" converts integer to uppercase hexa (10->A)
            line_str = "".join(f"{cell:X}" for cell in row)
            new_file.write(line_str + "\n")

        # mandatory empty line
        new_file.write("\n")

        # entrance coordinates
        new_file.write(f"{entry_coord[0]},{entry_coord[1]}\n")
        # exit coordinates
        new_file.write(f"{exit_coord[0]},{exit_coord[1]}\n")
        # path from entrance to exit
        new_file.write(f"{path}\n")
