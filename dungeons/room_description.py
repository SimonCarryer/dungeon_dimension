from string import Template
from random import Random

class RoomDescription():
    def __init__(self, first_sentence, ornaments=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.ornaments = ornaments
        self.paragraphs = [[first_sentence]]
        self.terms = {}
        if self.ornaments is not None:
            ornament, d = self.ornaments.ornament()
            for term, options in d.items():
                self.register_term(term, options)

    def register_term(self, term, options):
        self.terms[term] = options
        self.terms[term[0].upper() + term[1:]] =  [text[0].upper() + text[1:] for text in options]

    def add(self, sentence, terms=None, new_paragraph=False):
        if new_paragraph:
            self.paragraphs.append([sentence])
        else:
            self.paragraphs[-1].append(sentence)
        if terms is not None:
            for term, options in terms.items():
                self.register_term(term, options)

    def make_d(self):
        d = {}
        for t in self.terms:
            d[t] = self.random_state.choice(self.terms[t])
        return d

    def __iadd__(self, new_sentence):
        if new_sentence.__class__ == str:
            self.add(new_sentence)
            return self

    def __add__(self, new_sentence): # This should actually create a new instance, but it doesn't because I am lazy
        if new_sentence.__class__ == str:
            self.add(new_sentence)
            return self

    def __str__(self):
        if len(self.sentences) == 1 and self.ornaments is not None:
            ornament, d = self.ornaments.ornament()
            self.add(ornament, d)
        description = " ".join(self.sentences)
        while '$' in description:
            description = Template(description).substitute(self.make_d())
        return description

    def to_list(self):
        if len(self.paragraphs[0]) == 1 and self.ornaments is not None and len(self.paragraphs) == 1:
            ornament, d = self.ornaments.ornament()
            self.add(ornament, d)
        final = []
        for paragraph in self.paragraphs:
                p = " ".join(paragraph)
                while '$' in p:
                    p = Template(p).substitute(self.make_d())
                final.append(p)
        return final