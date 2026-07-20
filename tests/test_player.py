import sys
from pathlib import Path
from types import SimpleNamespace

from src.maze_app.display.player import Player

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class DummySpriteSheet:
    def __init__(self, path):
        self.path = path

    def get_texture_grid(self, size, columns, count):
        return [object() for _ in range(count)]


class DummyVisualizer:
    def __init__(self):
        self.map = SimpleNamespace(grid=[[(0, 0)]], cell=16, scale=1.0)
        self.entry = (0, 0)


def test_player_initializes_without_arcade_position_error(monkeypatch):
    monkeypatch.setattr("src.maze_app.display.player.arcade.SpriteSheet",
                        DummySpriteSheet)

    player = Player(DummyVisualizer())

    assert player.center_x == 0
    assert player.center_y == 0
