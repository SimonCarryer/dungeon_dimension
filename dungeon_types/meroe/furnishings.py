from dungeons.dungeon_furnisher import SpecialFurnishing
from .names import Namer
import yaml


with open('data/meroe/books.yaml', 'r') as f:
    books = yaml.load(f)

class Library(SpecialFurnishing):
    def add_special_furnishing(self, layout):
        rooms = [data for node, data in layout.nodes(data=True) if 'library' in data['tags'] or 'study' in data['tags']]
        for room in rooms:
            self.add_books(room, layout.theme)

    def add_books(self, room, dungeon_theme):
        namer = Namer(dungeon_theme, self.random_state)
        n_books = 3
        chosen_books = self.random_state.sample(books[dungeon_theme], n_books)
        room["library"] = [{"title": namer.add_names(book["title"]), "contents": namer.add_names(book["contents"])} for book in chosen_books]