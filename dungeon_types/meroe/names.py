import yaml
from string import Template

with open('data/meroe/names.yaml', 'r') as f:
    names = yaml.load(f)

with open('data/meroe/mummies.yaml', 'r') as f:
    mummies = yaml.load(f)

with open('data/meroe/crypts.yaml', 'r') as f:
    crypts = yaml.load(f)

class Namer:
    def __init__(self, theme, random_state):
        self.names = names[theme]["names"]
        self.gods = names[theme]["gods"]
        self.mummies = mummies[theme]
        self.random_state = random_state
        name = "".join([self.random_state.choice(self.names[i]) for i in ["first", "middle", "last"]])
        title = self.random_state.choice(self.names["title"])
        self.name = f"{title} {name}"

    def god(self):
        return self.random_state.choice(self.gods)

    def add_names(self, base_string):
        d = {"name": self.name, "god": self.god()}
        return Template(base_string).safe_substitute(d)

    def crypt(self):
        description = self.random_state.choice(crypts["entrance"]["description"])
        block = self.random_state.choice(crypts["entrance"]["blocked"])
        trap = self.random_state.choice(crypts["entrance"]["trapped"])
        key = self.random_state.choice(crypts["entrance"]["key"])
        entrance = self.add_names(" ".join([description, block, trap, key]))
        description = self.random_state.choice(crypts["crypt"]["description"])
        treasure = {"objects": [self.random_state.choice(crypts["crypt"]["valuables"])]}
        return {
            "entrance": entrance,
            "description": description + " In the middle of the room is a sarcophagus made of ${material}.",
            "treasure": treasure
        }

    def mummy(self):
        power = self.random_state.choice(self.mummies["powers"])
        defence = self.random_state.choice(self.mummies["protection"])
        appearance = self.random_state.choice(self.mummies["appearance"])
        name = self.name
        return {
            "description": f"Rising from the sarcophagus you see {appearance}. This is the mummy of {name}, with the following powers:",
            "name": name,
            "powers": [power, defence]
        }