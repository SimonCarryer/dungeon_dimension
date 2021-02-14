import yaml
from random import Random
from bisect import bisect_left
from string import Template
from encounters.encounter_api import EncounterSource

with open('data/traps.yaml') as f:
    attacks = {}
    saves = {}
    effects = {}
    triggers = {}
    telltales = {}
    trap_file = yaml.load(f)
    damage = trap_file['damage']
    for challenge in ['setback', 'dangerous', 'deadly']:
        attacks[challenge] = tuple([int(i) for i in trap_file['attack'][challenge].split(', ')])
        saves[challenge] = tuple([int(i) for i in trap_file['save'][challenge].split(', ')])
    for trap_class in ['mechanical', 'magical']:
        telltales[trap_class] = trap_file[trap_class]['telltales']
        effects[trap_class] = trap_file[trap_class]['effect']
        triggers[trap_class] = trap_file[trap_class]['trigger']

def get_trap_damage():
    return {"setback": "1d6", "dangerous": "2d6", "deadly": "3d6"}

def get_trap_effects(level, trap_class):
    levels = list(effects[trap_class].keys())
    idx = bisect_left(levels, level)
    return effects[trap_class][levels[idx]]


class Trap:
    def __init__(self, level, challenge=None, trap_class=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        if challenge is None:
            roll = self.random_state.randint(1, 6)
            if roll <= 3:
                self.challenge = 'setback'
            elif roll <= 5:
                self.challenge = 'dangerous'
            else:
                self.challenge = 'deadly'
        else:
            self.challenge = challenge
        if trap_class is None:
            self.trap_class = self.random_state.choice(['mechanical', 'magical'])
        else:
            self.trap_class = trap_class
        self.attack = self.choose_attack()
        self.damage = get_trap_damage()[self.challenge]
        self.trigger = self.random_state.choice(triggers[self.trap_class])
        self.telltale = self.random_state.choice(telltales[self.trap_class])
        effect = self.random_state.choice(get_trap_effects(self.level, self.trap_class))
        self.name = effect['name']
        self.template = Template('$name trap: Triggered by $trigger. Can be detected by noticing $telltale. ' + effect['effect'])

    def choose_attack(self):
        return self.random_state.randint(1, 4)

    def __str__(self):
        d = {
            'name': self.name,
            'telltale': self.telltale,
            'trigger': self.trigger,
            'damage': self.damage,
            'attack': self.attack,
        }
        return self.template.substitute(d)
        
