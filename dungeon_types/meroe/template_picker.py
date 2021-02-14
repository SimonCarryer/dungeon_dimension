from .dungeon_templates import *
from dungeons.dungeon_templates import PassingAgesTemplate
from random import Random

template_bunches = [
    [OriginalConstructionTemplate, MeroeAgeTemplate, CryptTemplate, LairTemplate],
    [OriginalConstructionTemplate, MeroeAgeTemplate, CryptTemplate, BanditsTemplate],
     [OriginalConstructionTemplate, MeroeAgeTemplate, CryptTemplate],
      [PlunderedOriginalConstructionTemplate, HabitationTemplate, MeroeAgeTemplate, LootedCryptTemplate, BanditsTemplate],
   [PlunderedOriginalConstructionTemplate, HabitationTemplate, MeroeAgeTemplate, LootedCryptTemplate],
   [PlunderedOriginalConstructionTemplate, HabitationTemplate, MeroeAgeTemplate, LootedCryptTemplate, LairTemplate],
      [PlunderedOriginalConstructionTemplate, HabitationTemplate, MeroeAgeTemplate, CryptTemplate, LairTemplate],
]

class MeroeTemplatePicker:
    def __init__(self, layout, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.type = layout.type
        self.them = layout.theme

    def pick_set(self):
        templates = self.random_state.choice(template_bunches)
        return templates