from .encounter_builder import EncounterBuilder
from .encounter_picker import EncounterPicker
from collections import Counter, defaultdict
import yaml
import random

with open('data/meroe/inhabitants.yaml', 'r') as f:
    monsters = yaml.load(f)

class EncounterSource:
    def __init__(self,
                monster_set=None,
                random_state=None):
        if random_state is None:
            self.random_state = random.Random()
        else:
            self.random_state = random_state
        self.monster_set = monster_set
        self.used_signs = set()
        monster_list = monsters[monster_set]['types']
        for monster in monster_list:
            monster["XP"] = monster["HD"] * 100
        self.encounter_builder = EncounterBuilder(500, monster_source=monster_list)
        self.encounter_picker = EncounterPicker(self.encounter_builder.monster_lists, 500)
        
    def get_encounter(self, difficulty=None, occurrence=None, style=None):
        response = {}
        encounter = self.encounter_picker.pick_encounter(difficulty=difficulty, occurrence=occurrence, style=style)
        stats = self.build_stat_blocks(encounter['monsters'])
        response['success'] = True
        response['monster_set'] = self.monster_set.title()
        response['monsters'] = [{'name': k, 'number': v, 'stats': stats[k]} for k, v in dict(Counter([monster['name'] for monster in encounter['monsters']])).items()]
        response['difficulty'] = encounter['difficulty']
        response['monster_hash'] = encounter['monster_hash']
        response['treasure'] = None
        return response

    def build_stat_blocks(self, list_of_monsters):
        stats = {}
        for monster in list_of_monsters:
            stat_block = f"HD {monster['HD']}, AC {monster['AC']}, Att. {monster['attack']}"
            if monster.get("special") is not None:
                stat_block += f", Special: {monster['special']}"
            stats[monster["name"]] = stat_block
        return stats
            

    def get_sign(self):
        signs = [sign for sign in monsters[self.monster_set]['signs'] if sign not in self.used_signs]
        if len(signs) > 0:
            sign = self.random_state.choice(signs)
            self.used_signs.add(sign)
        else:
            sign = None
        return sign

