from dungeons.dungeon_ornamentation import Ornamentation
from encounters.encounter_api import EncounterSource

def test_ornamentation():
    ornaments = Ornamentation("prison")
    ##print(ornaments.ornament())

def test_encounter_source_summary():
    source = EncounterSource(monster_set="jailers")
    print(source.get_encounter())
