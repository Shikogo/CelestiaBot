import json
from models import *

with open("./raw/pony_data.json") as f:
    ponies = json.load(f)

with open("./raw/creature_data.json") as f:
    creatures = json.load(f)

with db_session:
    for pony in ponies:
        Pony(**pony)
    for creature in creatures:
        Pony(**creature)
