from .dungeon_templates import *
from .dungeon_manager import DungeonManager
from .special_events import VillainHideout, LostItem, ForbiddingDoor, UnderdarkEntrance, NPCHome, TrapRoom

from random import Random

template_bunches = {
    'dungeon_dimension': [
        [PrisonTemplate, PassingAgesTemplate],
        [PrisonTemplate],
        [PrisonTemplate, OrganicTemplate],
        [OssuaryTemplate],
        [OssuaryTemplate, PassingAgesTemplate],
        [OssuaryTemplate, IncursionTemplate],
        [OssuaryTemplate, PassingAgesTemplate, IncursionTemplate],
        [OssuaryTemplate, OrganicTemplate]
    ]
}

class TemplatePicker:
    def __init__(self, layout, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.type = layout.type
        self.them = layout.theme

    def pick_set(self):
        templates = self.random_state.choice(template_bunches[self.type])
        return templates     

    def special_events(self):
        special_events = []
        if self.random_state.randint(1, 6) >= 7:
            n_events = 1
            events = self.random_state.sample([TrapRoom],n_events)
            special_events += events
        return [(i, None) for i in special_events]
