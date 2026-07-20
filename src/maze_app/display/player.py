import arcade


class Player(arcade.Sprite):
    def __init__(self, visualizer) -> None:
        self.visualizer = visualizer
        self.map = self.visualizer.map
        self.cell_pos = list(self.visualizer.entry)
        x, y = self.cell_pos
        cx, cy = self.map.grid[y][x]
        self.speed: int = self.map.cell // 16

        self.dx: int = 0
        self.dy: int = 0
        self.next_dx: int = 0
        self.next_dy: int = 0

        w = 96
        h = 320
        columns = 4
        sprite_path = "src/maze_app/display/sprite/player.png"
        self.sprite_sheet = arcade.SpriteSheet(sprite_path)
        all_textures = self.sprite_sheet.get_texture_grid(
            size=(w/columns, h/8),
            columns=columns,
            count=columns*8
        )

        self.anim_sud = all_textures[0:columns]
        self.anim_ouest = all_textures[columns*2:columns*3]
        self.anim_nord = all_textures[columns*4:columns*5]
        self.anim_est = all_textures[columns*6:columns*7]
        super().__init__(self.anim_sud[0])
        self.scale = self.visualizer.map.scale * 1.5
        self.center_x = cx
        self.center_y = cy

        self.current_frame = 0
        self.time_counter = 0.0
        self.animation_speed = 0.12

        self.current_anim_list = self.anim_sud[::4]

    def init_player(self) -> None:
        self.cell_pos = list(self.visualizer.entry)
        x, y = self.cell_pos
        cx, cy = self.map.grid[y][x]
        self.center_x = cx
        self.center_y = cy
        self.speed: int = self.map.cell // 16

        self.dx: int = 0
        self.dy: int = 0
        self.next_dx: int = 0
        self.next_dy: int = 0

        self.current_anim_list = self.anim_sud[::4]

    def update(self, delta_time: float) -> None:
        """Update the player's position and handle pac-gum collection.

        Advances the player toward the target cell, changes direction
        when the requested direction is not blocked by a wall, and
        collects a pac-gum or super pac-gum (triggering ``eat_super``)
        when the player reaches a cell that contains one.

        Returns:
            None
        """
        cx, cy = self.map.grid[self.cell_pos[1]][self.cell_pos[0]]
        if ([self.center_x, self.center_y] ==
           list(self.map.grid[self.cell_pos[1]][self.cell_pos[0]])):
            if not self.have_wall(self.next_dx, self.next_dy):
                self.dx = self.next_dx
                self.dy = self.next_dy

            if not self.have_wall(self.dx, self.dy):
                self.cell_pos[0] += self.dx
                self.cell_pos[1] -= self.dy
            else:
                self.texture = self.current_anim_list[0]
                return
        target = list(self.map.grid[self.cell_pos[1]][self.cell_pos[0]])
        if self.center_x < target[0]:
            self.current_anim_list = self.anim_ouest
            self.center_x = min(self.center_x + self.speed, target[0])
        elif self.center_x > target[0]:
            self.current_anim_list = self.anim_est
            self.center_x = max(self.center_x - self.speed, target[0])
        if self.center_y < target[1]:
            self.current_anim_list = self.anim_nord
            self.center_y = min(self.center_y + self.speed, target[1])
        elif self.center_y > target[1]:
            self.current_anim_list = self.anim_sud
            self.center_y = max(self.center_y - self.speed, target[1])

        self.time_counter += delta_time
        if self.time_counter >= self.animation_speed:
            self.time_counter = 0.0
            self.current_frame = ((self.current_frame + 1) %
                                  len(self.current_anim_list))
            self.texture = self.current_anim_list[self.current_frame]

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Record the requested movement direction from arrow key input.

        The requested direction is stored in ``next_dx``/``next_dy``
        and applied on the next ``update`` call if the corresponding
        path is not blocked by a wall.

        Args:
            key (int): The arcade key code that was pressed.
            modifiers (int): Bitwise combination of active modifier
                keys (e.g., Shift, Ctrl).

        Returns:
            None
        """
        if not self.visualizer.on_menu:
            if key == arcade.key.LEFT:
                self.next_dx = -1
                self.next_dy = 0
            elif key == arcade.key.RIGHT:
                self.next_dx = 1
                self.next_dy = 0
            elif key == arcade.key.UP:
                self.next_dx = 0
                self.next_dy = 1
            elif key == arcade.key.DOWN:
                self.next_dx = 0
                self.next_dy = -1

    def have_wall(self, nx: int, ny: int) -> bool:
        """Check whether a wall blocks the player's movement in a direction.

        Args:
            nx (int): Horizontal direction to test (``-1``, ``0``, or
                ``1``).
            ny (int): Vertical direction to test (``-1``, ``0``, or
                ``1``).

        Returns:
            bool: ``True`` if a wall blocks movement in that
            direction from the player's current cell, ``False``
            otherwise.
        """
        current = self.visualizer.maze[self.cell_pos[1]][self.cell_pos[0]]
        north = [1, 3, 5, 7, 9, 11, 13, 15]
        east = [2, 3, 6, 7, 10, 11, 14, 15]
        south = [4, 5, 6, 7, 12, 13, 14, 15]
        west = [8, 9, 10, 11, 12, 13, 14, 15]

        if nx == 1 and current in east:
            return True
        elif nx == -1 and current in west:
            return True
        elif ny == -1 and current in south:
            return True
        elif ny == 1 and current in north:
            return True

        return False
