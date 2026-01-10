import os
import sys

sys.path.append(os.path.abspath("."))

from src.core.contracts import InputEvent, Key, Renderer
from src.engine.game_loop import GameLoop
from src.engine.scene_manager import SceneManager
from src.scenes import utils
from src.scenes.scenes import MapScene, UIScene
from src.ui import Text
from src.world.npc_controller import NPCMapController
from src.world.sprites import NPCMapSprite, PCMapSprite, SpriteSheetDescriptor


class FakeTilemap:
    def __init__(self, pixel_size=(100, 100)):
        self.pixel_size = pixel_size

    def render(self, renderer, camera_offset=(0, 0)):
        return None

    def collides(self, hitbox):
        return False


class InteractionUIScene(UIScene):
    def build(self):
        return Text("Hello")


class InteractionController(NPCMapController):
    def __init__(self, npc, ui_scene):
        self.npc = npc
        self.ui_scene = ui_scene

    def on_enter(self):
        return None

    def on_exit(self):
        return None

    def update(self, delta_time, player):
        return None

    async def interact(self, player):
        from src.scenes.utils import spawn_ui

        await spawn_ui(self.ui_scene)


class TrackingMapScene(MapScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_calls = 0
        self.render_calls = 0

    def update(self, delta_time: float) -> None:
        self.update_calls += 1
        super().update(delta_time)

    def render(self, renderer: Renderer) -> None:
        self.render_calls += 1
        super().render(renderer)


class RecordingRenderer(Renderer):
    def __init__(self):
        self.present_calls = 0

    @property
    def size(self) -> tuple[int, int]:
        return (320, 240)

    def clear(self, color) -> None:
        return None

    def draw_rect(self, color, rect) -> None:
        return None

    def draw_rect_outline(self, color, rect, width: int = 1) -> None:
        return None

    def draw_image(self, image, source_rect, destination) -> None:
        return None

    def draw_text(self, text, position, color, font_size: int = 32, center: bool = False) -> None:
        return None

    def present(self) -> None:
        self.present_calls += 1


class FrameEventSource:
    def __init__(self, frames):
        self._frames = list(frames)

    def poll(self):
        if not self._frames:
            return []
        return self._frames.pop(0)


class FixedTimeSource:
    def tick(self, target_fps: int) -> float:
        return 0.016


def make_sprite(cls=PCMapSprite, **kwargs):
    descriptor = SpriteSheetDescriptor(
        image="image",
        frame_width=10,
        frame_height=10,
        columns=1,
        animations={"idle": {"down": [0]}, "walk": {"right": [0]}},
    )
    return cls(name=kwargs.pop("name", "hero"), spritesheet=descriptor, **kwargs)


def test_interaction_overlay_does_not_block_game_loop():
    tilemap = FakeTilemap()
    player = make_sprite()
    npc = NPCMapSprite(name="npc", spritesheet=player.spritesheet)
    npc.y = player.spritesheet.frame_height + 2
    ui_scene = InteractionUIScene()
    controller = InteractionController(npc=npc, ui_scene=ui_scene)
    scene = TrackingMapScene(tilemap, tilemap, player, npc_controllers=[controller])

    manager = SceneManager(initial_scene=scene)
    utils.register_scene_manager(manager)

    events = FrameEventSource(
        [
            [InputEvent(type="KEYDOWN", payload={"key": Key.ENTER})],
            [],
            [InputEvent(type="QUIT")],
        ]
    )
    renderer = RecordingRenderer()
    clock = FixedTimeSource()

    game_loop = GameLoop(manager, renderer, events, clock)

    game_loop.run()

    assert manager._overlay_scenes == [ui_scene]
    assert renderer.present_calls >= 2
    assert scene.update_calls >= 2

    scheduler = utils.get_scheduler()
    manager.pop_overlay(ui_scene)
    scheduler.tick()
    scheduler.loop.close()
