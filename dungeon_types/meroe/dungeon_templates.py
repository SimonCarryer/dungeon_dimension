from dungeons.dungeon_templates import DungeonBaseTemplate, NewInhabitantsTemplate, DungeonTemplate
from dungeons.dungeon_populator import Explorers, Lair
from dungeons.dungeon_ornamentation import Ornamentation
from traps.trap_api import TrapSource
from dungeons.special_events import SpecialRoom
from dungeons.room_description import RoomDescription
from .furnishings import Library
from .names import Namer


class OriginalConstructionTemplate(DungeonBaseTemplate):
    def alter_dungeon(self, layout):
        self.build_furnisher(self.type, self.theme).furnish(layout)
        Library().add_special_furnishing(layout)
        trap_source = TrapSource(1)
        self.build_populator(layout.theme, trap_source=trap_source, wandering=False).populate(layout)
        return layout

class PlunderedOriginalConstructionTemplate(DungeonBaseTemplate):
    def alter_dungeon(self, layout):
        self.build_furnisher(self.type, self.theme).furnish(layout)
        Library().add_special_furnishing(layout)
        trap_source = None
        self.build_populator(None, trap_source=trap_source, wandering=False).populate(layout)
        return layout

class MeroeAgeTemplate(DungeonTemplate):
    def alter_dungeon(self, layout):
        effects = ['earthquake', 'age']
        age_effect = self.random_state.choice(effects)
        self.build_ager(cause=age_effect).age(layout)

class HabitationTemplate(DungeonTemplate):
    def alter_dungeon(self, layout):
        self.build_ager(cause="habitation").age(layout)
         

class CryptTemplate(SpecialRoom):
    def find_best_room(self, layout):
        free_nodes = [node for node, data in layout.nodes(data=True) if 'important' in data.get('tags') and 'secret' not in data.get('tags')]
        if len(free_nodes) > 0:
            return self.random_state.choice(free_nodes)
        else:
            return self.random_state.choice([node for node, data in layout.nodes(data=True) if 'important' in data.get('tags') ])

    def alter_dungeon(self, layout):
        namer = Namer(layout.theme, self.random_state)
        details = namer.crypt()
        room_description = RoomDescription(details["description"], ornaments=Ornamentation(layout.purpose, layout.theme))
        mummy = namer.mummy()
        room_description.add(mummy["description"], new_paragraph=True)
        for power in mummy["powers"]:
            room_description.add(power, new_paragraph=True)
        encounter = {}
        layout.name = f"Tomb of {mummy['name']}"
        encounter['monster_set'] = "Mummy"
        encounter['monsters'] = [{'name': "Mummy", 'number': 1, 'stats': '4 HD, attack 1d8/1d8 sword/other'}]
        self.add_room(
                 layout,
                 secret=False,
                 passage_description=details["entrance"],
                 room_description=room_description,
                 room_encounter=encounter,
                 room_tags=None,
                 room_treasure=details["treasure"],
                 room_link=None,
                 connection_weight=4,
                 room_name="Crypt")
        return layout

class LootedCryptTemplate(CryptTemplate):
    def alter_dungeon(self, layout):
        namer = Namer(layout.theme, self.random_state)
        details = namer.crypt()
        room_description = RoomDescription(details["description"], ornaments=Ornamentation(layout.purpose, layout.theme))
        mummy = namer.mummy()
        room_description.add("Whatever magic or treasure was once in this room, it has vanished long ago.")
        layout.name = f"Tomb of {mummy['name']}"
        self.add_room(
                 layout,
                 secret=False,
                 passage_description='',
                 room_description=room_description,
                 room_encounter=None,
                 room_tags=None,
                 room_treasure=None,
                 room_link=None,
                 connection_weight=1,
                 room_name="Crypt")
        return layout

class BanditsTemplate(NewInhabitantsTemplate):
    def alter_dungeon(self, layout):
        self.make_an_entrance(layout)
        self.build_populator('bandits', populator_method=Explorers).populate(layout)
        return layout


class LairTemplate(NewInhabitantsTemplate):
    def alter_dungeon(self, layout):
        self.make_an_entrance(layout)
        self.build_populator('beasts', populator_method=Lair, wandering=False).populate(layout)
        return layout
