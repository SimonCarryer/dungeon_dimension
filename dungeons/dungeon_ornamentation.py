import yaml
from random import Random
from string import Template

with open('data/meroe/themes.yaml', 'r') as f:
    themes = yaml.load(f)

with open('data/meroe/ornamentation.yaml', 'r') as f:
    ornaments = yaml.load(f)

class Ornamentation():
    def __init__(self, purpose, theme, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.theme = themes[theme]

    def ornament(self):
        if self.random_state.randint(1, 6) >= 5:
            template = "${extra}"
        else:
            template = self.random_state.choice(ornaments)
        d = {}
        for key in list(self.theme.keys()):
            d[key[:-1]] = self.theme[key]
        return template, d