class Visualizer:
    def __init__(self, output_file: str):
        self.maze: list = []
        self.maze_width: int = 0
        self.maze_height: int = 0
        self.entry: list = [0, 0]
        self.exit: list = [0, 0]
        self.path: str = []
        self.have_path: bool = False

        self.output_parser(output_file)

    def output_parser(self, output_file: str):
        try:
            with open(output_file, "r") as file:
                content = file.read().splitlines()
        except OSError as e:
            raise OSError(f"File not found : {e}")

        i = 0
        while (content[i] != ""):
            self.maze.append(content[i])
            i += 1
        # print(self.maze)

        self.maze_width = len(content[0])
        # print(self.maze_width)

        self.maze_height = i
        # print(self.maze_height)

        i += 1
        coord = content[i].split(",")
        self.entry = [int(coord[1]), int(coord[0])]
        # print(self.entry)

        i += 1
        coord = content[i].split(",")
        self.exit = [int(coord[1]), int(coord[0])]
        # print(self.exit)

        i += 1
        self.path = content[i]
        # print(self.path)
