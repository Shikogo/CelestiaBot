from pony.orm import *

db = Database()

class Pony(db.Entity):
    name = Required(str)
    kind = Optional(str)
    group = Optional(str)
    coat_color = Optional(str)
    coat_color_name = Optional(str)
    mane_color = Optional(str)
    mane_color_name = Optional(str)
    eye_color = Optional(str)
    eye_color_name = Optional(str)
    first_appearance = Optional(str)
    link = Optional(str)
    image = Required(str)
    official = Required(bool)

db.bind(provider="sqlite", filename="ponies.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
