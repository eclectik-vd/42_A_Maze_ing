from typing import TYPE_CHECKING, List, Any
import arcade

if TYPE_CHECKING:
    from src.maze_app.display.arcade_visualizer import ArcadeVisualizer


class Player(arcade.Sprite):
    """Player sprite with collision detection and animation.

    Represents the player character in the maze game. Handles movement
    via keyboard input, wall collision detection, cell-based positioning
    with smooth pixel-based animation, and sprite animation cycling.
    Extends arcade.Sprite for rendering and arcade integration.

    Attributes:
        visualizer: Reference to the arcade visualizer.
        map: Reference to the Map object for grid and collision data.
        cell_pos (list[int]): Current cell coordinates [x, y].
        speed (int): Pixels to move per frame.
        dx (int): Current movement direction x component.
        dy (int): Current movement direction y component.
        next_dx (int): Requested next movement x component.
        next_dy (int): Requested next movement y component.
        sprite_sheet (arcade.SpriteSheet): Loaded player sprite sheet.
        anim_sud (list[arcade.Texture]): South-facing animation frames.
        anim_ouest (list[arcade.Texture]): West-facing animation frames.
        anim_nord (list[arcade.Texture]): North-facing animation frames.
        anim_est (list[arcade.Texture]): East-facing animation frames.
        current_frame (int): Current animation frame index.
        time_counter (float): Time accumulator for frame timing.
        animation_speed (float): Time per frame in seconds.
        current_anim_list (list[arcade.Texture]): Currently active animation.
    """

    def __init__(self, visualizer: "ArcadeVisualizer") -> None:
        """Initialize the player sprite with animations and starting position.

        Loads the player sprite sheet, extracts animation frames for each
        direction, initializes position at the maze entry point, and sets up
        movement and animation state.

        Args:
            visualizer: The arcade visualizer instance (ArcadeVisualizer).
        """
        self.visualizer: "ArcadeVisualizer" = visualizer
        self.map: Any = self.visualizer.map
        self.cell_pos: List[int] = list(self.visualizer.entry)
        x: int
        y: int
        x, y = self.cell_pos
        cx: int
        cy: int
        cx, cy = self.map.grid[y][x]
        self.speed: int = self.map.cell // 16

        self.dx: int = 0
        self.dy: int = 0
        self.next_dx: int = 0
        self.next_dy: int = 0

        w: int = 96
        h: int = 320
        columns: int = 4
        sprite_path: str = "src/maze_app/display/sprite/player.png"
        self.sprite_sheet: arcade.SpriteSheet = arcade.SpriteSheet(sprite_path)
        all_texture: List[arcade.Texture] = self.sprite_sheet.get_texture_grid(
            size=(int(w/columns), int(h/8)),
            columns=columns,
            count=columns*8
        )

        self.anim_sud: List[arcade.Texture] = all_texture[0:columns]
        self.anim_ouest: List[arcade.Texture] = all_texture[columns*2:
                                                            columns*3]
        self.anim_nord: List[arcade.Texture] = all_texture[columns*4:
                                                           columns*5]
        self.anim_est: List[arcade.Texture] = all_texture[columns*6:columns*7]

        win_w: int = 288
        win_h: int = 320
        win_columns = 12
        win_sprite_path: str = "src/maze_app/display/sprite/win.png"
        self.win_sprite_sheet: arcade.SpriteSheet =\
            arcade.SpriteSheet(win_sprite_path)
        win_textures: List[arcade.Texture] =\
            self.win_sprite_sheet.get_texture_grid(
            size=(int(win_w/win_columns), int(win_h/8)),
            columns=win_columns,
            count=win_columns*8
        )
        self.anim_win: List[arcade.Texture] = win_textures[win_columns:
                                                           win_columns*3]
        super().__init__(self.anim_sud[0])
        self.scale = self.visualizer.map.scale * 1.5
        self.center_x = cx
        self.center_y = cy

        self.current_frame: int = 0
        self.time_counter: float = 0.0
        self.animation_speed: float = 0.12

        self.current_anim_list: List[arcade.Texture] = self.anim_sud[::4]

    def init_player(self) -> None:
        """Reset player position and movement state to initial state.

        Called when regenerating or restarting the maze. Resets the player
        cell position to the maze entry point, clears all movement vectors,
        and resets animation to the south-facing idle state.

        Returns:
            None: Modifies player position and state variables in place.
        """
        self.cell_pos = list(self.visualizer.entry)
        x: int
        y: int
        x, y = self.cell_pos
        cx, cy = self.map.grid[y][x]
        self.center_x = cx
        self.center_y = cy
        self.speed = self.map.cell // 16

        self.dx = 0
        self.dy = 0
        self.next_dx = 0
        self.next_dy = 0

        self.current_anim_list = self.anim_sud[::4]

    def update(self, delta_time: float = 0.0) -> None:
        """Update player position, direction, and animation each frame.

        Checks if player has reached the target cell center. If so, applies
        the queued direction if not blocked by walls, otherwise keeps current
        direction. Smoothly interpolates pixel position toward target cell
        center. Updates animation frame based on elapsed time.

        Args:
            delta_time (float): Time elapsed since last frame in seconds.

        Returns:
            None: Modifies position, animation state, and counters in place.
        """
        cx: int
        cy: int
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
        target: List[int] = list(self.map.grid[self.cell_pos[1]]
                                 [self.cell_pos[0]])
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

        ex: int
        ey: int
        cex: int
        cey: int
        cex, cey = self.visualizer.exit
        ex, ey = self.map.grid[cey][cex]
        if self.center_x == ex and self.center_y == ey:
            self.dx == 0
            self.dy == 0
            self.next_dx = 0
            self.next_dy = 0
            self.current_anim_list = self.anim_win

        self.time_counter += delta_time
        if self.time_counter >= self.animation_speed:
            self.time_counter = 0.0
            self.current_frame = ((self.current_frame + 1) %
                                  len(self.current_anim_list))
            self.texture = self.current_anim_list[self.current_frame]

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Record the requested movement direction from arrow key input.

        Records the desired movement direction in next_dx/next_dy when arrow
        keys are pressed during gameplay (not menu mode). The direction is
        applied on the next update call if not blocked by a wall.

        Args:
            key (int): The arcade key code that was pressed.
            modifiers (int): Bitwise combination of active modifier keys.

        Returns:
            None: Modifies next_dx and next_dy based on key input.
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

        Examines the current cell's wall encoding and checks if the
        requested direction is blocked. The maze cell encoding uses
        bits to represent walls (N/E/S/W), which are then matched
        against the direction being tested.

        Args:
            nx (int): Horizontal direction to test (-1, 0, or 1).
            ny (int): Vertical direction to test (-1, 0, or 1).

        Returns:
            bool: True if a wall blocks movement in that direction,
                False otherwise.
        """
        current: int = self.visualizer.maze[self.cell_pos[1]][self.cell_pos[0]]
        north: List[int] = [1, 3, 5, 7, 9, 11, 13, 15]
        east: List[int] = [2, 3, 6, 7, 10, 11, 14, 15]
        south: List[int] = [4, 5, 6, 7, 12, 13, 14, 15]
        west: List[int] = [8, 9, 10, 11, 12, 13, 14, 15]

        if nx == 1 and current in east:
            return True
        elif nx == -1 and current in west:
            return True
        elif ny == -1 and current in south:
            return True
        elif ny == 1 and current in north:
            return True
        return False
