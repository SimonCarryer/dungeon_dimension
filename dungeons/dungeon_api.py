from .dungeon import Dungeon
from .dungeon_layout import DungeonLayout
from .dungeon_templates import *
from .dungeon_manager import DungeonManager
from .dungeon_template_picker import TemplatePicker
from dungeon_types.meroe.template_picker import MeroeTemplatePicker

class DungeonSource():
    def __init__(self, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = 1
        n_rooms = self.random_state.randint(3, 5)
        layout = DungeonLayout(n_rooms=n_rooms, secret_chance=8, random_state=self.random_state)
        layout.type = "meroe"
        layout.theme = self.random_state.choice(["golden age", "sun worship", "fallen age"])
        templates = MeroeTemplatePicker(layout, random_state=self.random_state).pick_set()
        with DungeonManager(self.level, layout, terrain="forest", random_state=self.random_state) as dungeon_manager:
            for template in templates:
                template(layout,
                         dungeon_manager=dungeon_manager,
                         random_state=self.random_state).alter_dungeon(layout)
        self.dungeon = Dungeon(layout, random_state=self.random_state)

    def get_dungeon(self):
        return self.dungeon.module()



