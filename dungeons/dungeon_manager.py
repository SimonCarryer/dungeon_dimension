from encounters.encounter_api import EncounterSource
from encounters.wandering_monsters import WanderingMonsters
from random import Random
from json import JSONEncoder
import logging
import yaml

with open('data/meroe/inhabitants.yaml', encoding='utf-8') as f:
    inhabitants = yaml.load(f.read())
    valuables = {k: inhabitants[k]["valuables"] for k in inhabitants}

logger = logging.getLogger(__name__)

class Sign():
    def __init__(self, sign):
        self.sign = sign

    def __str__(self):
        if self.sign:
            return self.sign
        else:
            return ''

    def delete(self):
        self.sign = None

class Treasure(dict):
    def __init__(self, manager, treasure_type, random_state):
        self.treasure_type = treasure_type
        self.random_state = random_state
        self.manager = manager
        self['objects'] = []

    def get_item(self):
        self['empty'] = False
        possibles = [item for item in valuables[self.treasure_type] if item not in self.manager.items]
        if len(possibles) == 0:
            possibles = valuables[self.treasure_type]
        self['objects'].append(self.random_state.choice(possibles + self.manager.items))
        self.manager.items = [item for item in self.manager.items if item not in self["objects"]]
        
    def clear_items(self):
        self['empty'] = True
        self.manager.items += self["objects"]
        self['objects'] = []


class TreasureManager:
    def __init__(self, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.valuables = valuables
        self.items = []
        self.treasures = []
        self.shares = []

    def get_treasure(self, shares=1, treasure_type=None):
        treasure = Treasure(self, treasure_type, self.random_state)
        self.treasures.append(treasure)
        for _ in range(shares+2):
            self.shares.append(treasure)
        self.assign_items()
        return treasure
    
    def clear_all(self):
        for treasure in self.treasures:
            treasure.clear_items()

    def assign_items(self):
        self.clear_all()
        self.random_state.shuffle(self.shares)
        n_shares = len(self.shares)
        for idx in range(n_shares):
            self.shares[idx % n_shares].get_item()

    def delete_treasure(self, treasure_to_delete):
        treasure_to_delete.clear_items()
        self.treasures = [treasure for treasure in self.treasures if treasure is not treasure_to_delete]
        self.shares = [share for share in self.shares if share is not treasure_to_delete]
        if len(self.treasures) > 0:
            self.assign_items()

class DungeonManager:
    def __init__(self, level, layout, terrain=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        self.layout = layout
        self.encounter_sources = {}
        self.encounters = {}
        self.signs = {}
        self.treasure_manager = TreasureManager(random_state=self.random_state)
        self.terrain = terrain
        self.events = []

    def add_encounter_source(self, source_name, monster_set, event_description, wandering=False):
        logger.debug('Adding encounter source %s (%s)' % (source_name, monster_set))
        encounter_source = EncounterSource(monster_set=monster_set,
                                    random_state=self.random_state)
        self.encounter_sources[source_name] = encounter_source
        self.encounters[source_name] = 0
        self.signs[source_name] = []
        self.add_event(source_name, event_description, monster_set, wandering=wandering)

    def add_special_encounter_source(self, source_name, encounter_source):
        logger.debug('Adding special encounter source %s' % (source_name))
        self.encounter_sources[source_name] = encounter_source
        self.encounters[source_name] = 0
        self.signs[source_name] = []        

    def add_event(self, source_name, description, monster_set, wandering=False):
        logger.debug('Adding event for source %s (%s)' % (source_name, monster_set))
        event = {
            'event': description,
            'monster_set': monster_set,
            'source_name': source_name
        }
        self.events.append(event)

    def get_encounter(self, source_name, **kwargs):
        logger.debug('Getting encouter from encounter source %s' % (source_name))
        encounter = self.encounter_sources[source_name].get_encounter(**kwargs)
        if encounter.get('success'):
            self.encounters[source_name] += 1
            encounter['source name'] = source_name
            return encounter
        else:
            return None

    def delete_encounter(self, encounter):
        logger.debug('Deleting encouter from encounter source %s' % (encounter.get('source name')))
        source_name = encounter.get('source name')
        self.encounters[source_name] -= 1

    def get_sign(self, source_name):
        logger.debug('Getting sign from encounter source %s' % (source_name))
        sign = Sign(self.encounter_sources[source_name].get_sign())
        self.signs[source_name].append(sign)
        return sign

    def delete_signs(self, source_name):
        logger.debug('Deleting sign from encounter source %s' % (source_name))
        for sign in self.signs[source_name]:
            sign.delete()

    def __enter__(self, *args):
        return self

    def get_treasure(self, shares=1, treasure_type=None):
        if treasure_type is None:
            treasure_type = self.layout.theme
        return self.treasure_manager.get_treasure(shares, treasure_type=treasure_type)

    def delete_treasure(self, treasure_to_delete):
        self.treasure_manager.delete_treasure(treasure_to_delete)

    def get_monster_sets(self, **kwargs):
        return self.monster_manual.get_monster_sets(**kwargs)

    def parse_event(self, event):
        text = event['event']
        monster_set = event['monster_set']
        return f'{text}: ({monster_set})'

    def __exit__(self, eType, eValue, eTrace):
        logger.debug('Exiting dungeon manager')
        for source_name in self.encounter_sources:
            if self.encounters[source_name] == 0:
                self.delete_signs(source_name)
        self.layout.terrain = self.terrain
        self.layout.level = self.level

        