from .dungeon_populator import Lair, OriginalInhabitants, UndergroundNatives, Explorers, Taint
from .dungeon_ager import DungeonAger
from encounters.encounter_api import EncounterSource
from .dungeon_furnisher import DungeonFurnisher
from random import Random
import yaml
import uuid
import logging
from traps.trap_api import TrapSource

with open('data/dungeon_age.yaml', 'r') as f:
    dungeon_age = yaml.load(f)
    effects = []
    for cause in dungeon_age.keys():
        for idx, room_effect in enumerate(dungeon_age[cause]['rooms']):
            if cause in ['earthquake', 'cave-age']:
                effects.append(room_effect)

logger = logging.getLogger(__name__)

class NoEncountersSource:
    def __init__(self):
        self.monster_set = None

    def get_encounter(*args, **kwargs):
        return {'success': False}

    def get_sign(self, name=None):
        return 'The accumulated dust of many ages.' # TODO: Make this better.

class DungeonTemplate:
    def __init__(self, layout, dungeon_manager=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.dungeon_manager = dungeon_manager
        self.name = str(uuid.uuid4())
        self.type = layout.type
        self.theme = layout.theme

    def build_populator(self, monster_set=None, populator_method=OriginalInhabitants, trap_source=None, wandering=True):
        if monster_set is None:
            encounter_source = NoEncountersSource()
            logger.debug('Making a NoEncounterSource')
            self.dungeon_manager.add_special_encounter_source(self.name, encounter_source)
        else:
            self.dungeon_manager.add_encounter_source(self.name, monster_set, self.event_type(monster_set), wandering=wandering)
        populator = populator_method(name=self.name,
                                     monster_set=monster_set,
                                     dungeon_manager=self.dungeon_manager,
                                     trap_source=trap_source,
                                     random_state=self.random_state)
        return populator
    
    def build_ager(self, cause):
        return DungeonAger(cause=cause, random_state=self.random_state)

    def event_type(self, monster_set=None):
        return 'Home to some scary monsters'

class DungeonBaseTemplate(DungeonTemplate):
    def event_type(self, monster_set=None):
        return 'Guarded by remnants of the original inhabitants'

    def build_furnisher(self, dungeon_type, dungeon_theme):
        return DungeonFurnisher(dungeon_type, dungeon_theme, random_state=self.random_state)

class PrisonTemplate(DungeonBaseTemplate):
    def alter_dungeon(self, layout):
        self.build_furnisher('prison').furnish(layout)
        trap_source = TrapSource(self.level)
        self.build_populator('jailers', trap_source=trap_source, wandering=False).populate(layout)
        return layout

class OssuaryTemplate(DungeonBaseTemplate):
    def alter_dungeon(self, layout):
        self.build_furnisher('ossuary').furnish(layout)
        trap_source = TrapSource(self.level)
        self.build_populator('dead', trap_source=trap_source, wandering=False).populate(layout)
        return layout


class IncursionTemplate(DungeonTemplate):
    def get_monster_sets(self):
        return 'jailers'

    def make_an_entrace(self, layout, tag='entrance'):
        free_rooms = [room for room, data in layout.nodes(data=True) if 'uninhabitable' not in data['tags']]
        new_entrance = self.random_state.choice(free_rooms)
        layout.node[new_entrance]['description'] += "A red door in one wall of this room leads to somewhere else in the dungeon dimension."

    def alter_dungeon(self, layout):
        self.make_an_entrace(layout)
        self.build_populator(self.get_monster_sets(), populator_method=Explorers).populate(layout)
        return layout

class xxx(DungeonTemplate):
    def event_type(self, monster_set=None):
        return 'Now home to new creatures'

    def free_rooms(self, layout):
        return [room for room, data in layout.nodes(data=True) if 'uninhabitable' not in data['tags']]

    def free_entrances(self, layout, tag='entrance'):
        return [room for room, data in layout.nodes(data=True) if tag in data['tags'] and 'uninhabitable' not in data['tags']]

    def make_an_entrace(self, layout, tag='entrance'):
        if len(self.free_entrances(layout, tag=tag)) == 0:
            free_rooms = self.free_rooms(layout)
            if len(free_rooms) > 0:
                new_entrance = self.random_state.choice(free_rooms)
                entrance_effects = [effect for effect in effects if tag in effect.get('tags', [])]
                effect = self.random_state.choice(entrance_effects)
                layout.node[new_entrance]['tags'] += [tag]
                current_description = layout.node[new_entrance].get('description', '')
                layout.node[new_entrance]['description'] = ' '.join([current_description, effect['description']])

class NewInhabitantsTemplate(DungeonTemplate):
    def event_type(self, monster_set=None):
        return 'Now home to new creatures'

    def free_rooms(self, layout):
        return [room for room, data in layout.nodes(data=True) if 'uninhabitable' not in data['tags']]

    def free_entrances(self, layout, tag='entrance'):
        return [room for room, data in layout.nodes(data=True) if tag in data['tags'] and 'uninhabitable' not in data['tags']]

    def make_an_entrance(self, layout, tag='entrance'):
        if len(self.free_entrances(layout, tag=tag)) == 0:
            free_rooms = self.free_rooms(layout)
            if len(free_rooms) > 0:
                new_entrance = self.random_state.choice(free_rooms)
                effect = "A tunnel has been dug from this room to the surface."
                layout.node[new_entrance]['description'] += effect

class HauntedTombTemplate(DungeonBaseTemplate):
    def event_type(self, monster_set=None):
        return 'Haunted by the unquiet dead'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['undead', 'immortal', 'guardian'])

    def alter_dungeon(self, layout):
        self.build_furnisher('tomb').furnish(layout)
        trap_source = TrapSource(self.level)
        self.build_populator(self.get_monster_sets(), trap_source=trap_source, wandering=False).populate(layout)
        return layout

class InfestedSewerTemplate(DungeonBaseTemplate):
    def event_type(self, monster_set=None):
        return 'Infested by unsettling creatures'

    def get_monster_sets(self):
        return ['sewers'] #self.monster_sets(required_tags=['urban', 'beast'])

    def alter_dungeon(self, layout):
        self.build_furnisher('sewer').furnish(layout)
        self.build_ager(cause='flood').age(layout)
        self.build_populator(self.get_monster_sets(), wandering=False).populate(layout)
        return layout

class EmptyTombTemplate(DungeonBaseTemplate):
    def event_type(self, monster_set=None):
        return 'Long forgotten'

    def get_monster_sets(self):
        return []

    def alter_dungeon(self, layout):
        self.build_furnisher('tomb').furnish(layout)
        trap_source = TrapSource(self.level)
        self.build_populator(None, trap_source=trap_source, wandering=False).populate(layout)
        return layout

class AbandonedStrongholdTemplate(DungeonBaseTemplate):
    def alter_dungeon(self, layout):
        self.build_furnisher('stronghold').furnish(layout)
        trap_source = TrapSource(self.level, trap_class='mechanical', random_state=self.random_state)
        populator = self.build_populator(monster_sets=None, trap_source=trap_source)
        populator.populate(layout)
        return layout

class DefendedStrongholdTemplate(DungeonBaseTemplate):
    def event_type(self, monster_set=None):
        return 'Guarded by fierce defenders'

    def get_monster_sets(self):
        return self.monster_sets(any_tags=['humanoid', 'giant'], none_tags=['savage', 'disorganised', 'rare', 'underdark'])

    def alter_dungeon(self, layout):
        self.build_furnisher('stronghold').furnish(layout)
        trap_source = TrapSource(self.level, trap_class='mechanical', random_state=self.random_state)
        populator = self.build_populator(self.get_monster_sets(), trap_source=trap_source, wandering=True)
        populator.populate(layout)
        return layout

class GuardedTreasureVaultTemplate(DungeonBaseTemplate):
    def event_type(self, monster_set=None):
        if monster_set is not None:
            rumour = self.get_rumour(monster_set, 'guarded')
        if rumour is None or monster_set is None:
            rumour = 'Guarded by ancient wards'
        return rumour

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['immortal', 'guardian'], none_tags=['undead'])

    def alter_dungeon(self, layout):
        self.build_furnisher('treasure vault').furnish(layout)
        trap_source = TrapSource(self.level)
        self.build_populator(self.get_monster_sets(), trap_source=trap_source, wandering=False).populate(layout)
        return layout

class AbandonedMineTemplate(DungeonBaseTemplate):
    def alter_dungeon(self, layout):
        self.build_furnisher('mine').furnish(layout)
        return layout

class AncientRemnantsTempleTemplate(DungeonBaseTemplate):
    def event_type(self, monster_set=None):
        return 'Still inhabited by traces of ancient worship'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['immortal'], any_tags=['evil', 'magical'], none_tags=['underdark'])
    
    def alter_dungeon(self, layout):
        self.build_furnisher('temple').furnish(layout)
        trap_source = TrapSource(self.level, trap_class='magical')
        self.build_populator(self.get_monster_sets(), trap_source=trap_source, wandering=True).populate(layout)
        return layout

class InUseTempleTemplate(DungeonBaseTemplate):
    def event_type(self, monster_set=None):
        return 'Protected by fanatical worshipers'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['humanoid'], any_tags=['evil', 'magical'], none_tags=['underdark'])

    def alter_dungeon(self, layout):
        self.build_furnisher('temple').furnish(layout)
        trap_source = TrapSource(self.level)
        self.build_populator(self.get_monster_sets(), trap_source=trap_source).populate(layout)
        return layout

class InfestedCaveTemplate(DungeonBaseTemplate):
    def event_type(self, monster_set=None):
        return 'Home to cave-dwelling creatures'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['cave-dweller'], none_tags=['rare', 'underdark'])

    def alter_dungeon(self, layout):
        self.build_furnisher('cave').furnish(layout)
        self.build_ager(cause='cave-age').age(layout)
        self.build_populator(self.get_monster_sets(), populator_method=UndergroundNatives).populate(layout)
        return layout

class DeepCaveTemplate(DungeonBaseTemplate):
    def event_type(self, monster_set=None):
        return 'Home to cave-dwelling creatures'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['cave-dweller'], none_tags=['rare'])

    def alter_dungeon(self, layout):
        self.build_furnisher('cave').furnish(layout)
        self.build_populator(self.get_monster_sets(), populator_method=OriginalInhabitants).populate(layout)
        return layout

class HauntedTemplate(DungeonTemplate):
    def event_type(self, monster_set=None):
        return 'Haunted by ghosts of the past'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['undead'], none_tags=['guardian'])
    
    def alter_dungeon(self, layout):
        self.build_ager('shadowfell').age(layout)
        self.build_populator(self.get_monster_sets(), populator_method=Taint, wandering=False).populate(layout, tag='shadowfell')
        return layout

class CursedTemplate(DungeonTemplate):
    def event_type(self, monster_set=None):
        return 'Cursed by an evil presence'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['evil', 'magical'])
    
    def alter_dungeon(self, layout):
        cause = self.random_state.choice(['illusion', 'shadowfell'])
        self.build_ager(cause).age(layout)
        self.build_populator(self.get_monster_sets(), populator_method=Taint, wandering=True).populate(layout, tag=cause)
        return layout


class OrganicTemplate(DungeonTemplate):
    def event_type(self, monster_set=None):
        return 'Tainted by contact from the Far Realms'

    def get_monster_sets(self):
        return 'organics'
    
    def alter_dungeon(self, layout):
        self.build_ager('organic').age(layout)
        self.build_populator(self.get_monster_sets(), populator_method=Taint, wandering=True).populate(layout, tag='aberration')
        return layout

class FeywildTemplate(DungeonTemplate):
    def event_type(self, monster_set=None):
        return 'A crossing-point to the Feywild'

    def get_monster_sets(self):
        return monster_manual.get_monster_sets(all_tags=['fey'])
    
    def alter_dungeon(self, layout):
        self.build_ager('illusion').age(layout)
        self.build_populator(monster_sets=self.get_monster_sets(), populator_method=OriginalInhabitants, wandering=True).populate(layout)
        return layout

class VolcanicTemplate(DungeonTemplate):
    def event_type(self, monster_set=None):
        return 'Near-destroyed by volcanic activity'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['fire'])

    def alter_dungeon(self, layout):
        self.build_ager('volcano').age(layout)
        self.build_populator(self.get_monster_sets(), populator_method=Taint).populate(layout, tag='fire')
        return layout

class InfestedTemplate(NewInhabitantsTemplate):
    def event_type(self, monster_set=None):
        return 'Infested with subterranean fauna'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['cave-dweller'], none_tags=['underdark', 'rare'])

    def alter_dungeon(self, layout):
        monster_sets = self.get_monster_sets()
        if layout.purpose == 'cave':
            age_effect = 'cave-age'
        else:
            age_effect = self.random_state.choice(['earthquake', 'age'])
        self.build_ager(age_effect).age(layout)
        self.make_an_entrace(layout, tag='cave-entrance')
        self.build_populator(monster_sets, populator_method=UndergroundNatives, wandering=True).populate(layout)
        return layout

class LairTemplate(NewInhabitantsTemplate):
    def event_type(self, monster_set=None):
        if monster_set is not None:
            rumour = self.get_rumour(monster_set, 'lair')
        if rumour is None or monster_set is None:
            rumour = 'A lair for beasts from the surrounding area'
        return rumour


    def get_monster_sets(self):
        return self.monster_sets(required_tags=['beast'], none_tags=['underdark'])

    def alter_dungeon(self, layout):
        self.make_an_entrace(layout)
        monster_sets = self.get_monster_sets()
        self.build_populator(monster_sets, populator_method=Lair, wandering=False).populate(layout)
        return layout


class ExplorerTemplate(NewInhabitantsTemplate):
    def event_type(self, monster_set=None):
        if monster_set is not None:
            rumour = self.get_rumour(monster_set, 'explorers')
        if rumour is None or monster_set is None:
            rumour = 'A lair for marauders and savages'
        return rumour

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['dungeon-explorer'], none_tags=['underdark'])

    def alter_dungeon(self, layout):
        self.make_an_entrace(layout)
        self.build_populator(self.get_monster_sets(), populator_method=Explorers).populate(layout)
        return layout

class SewerExplorerTemplate(ExplorerTemplate):
    def get_monster_sets(self):
        return self.monster_sets(required_tags=['dungeon-explorer', 'urban'], none_tags=['underdark']) 

class PassingAgesTemplate(DungeonTemplate):
    def get_monster_sets(self):
        return []

    def alter_dungeon(self, layout):
        effects = ['earthquake', 'habitation']
        if layout.purpose == 'cave':
            effects.append('cave-age')
        else: 
            effects.append('age')
        age_effect = self.random_state.choice(effects)
        self.build_ager(cause=age_effect).age(layout)
