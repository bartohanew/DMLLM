from .common import *
from .knowledge import Knowledge

class Location(Knowledge):
    questions = {
        "name": "Give a short name for this location.",
        "description": "Describe the location. What does it look like? What is it like to be there? What is the atmosphere?",
        "exits": "What exits are there from this location? The response should be a list of JSON objects, each with the following keys: location_description, obstacles, story_importance.",
    }

    attribute_prompt = flatten_whitespace(f"""
        Your role in life is to imagine a location, in a tabletop RPG.
    """)

    @classmethod
    def new_from_description(cls, description, story_importance):

        knowledge_type = cls.__name__.lower()
        cid = db[knowledge_type].insert_one({}).inserted_id
        c = cls(cid)
        c.set('description', description)
        c.set('story_importance', story_importance)

        for q in cls.questions:
            c.query(q)

        return c

if __name__ == "__main__":
    import sys
    e = Location.new_from_description(sys.argv[1], story_importance=sys.argv[2])
    print(e)
    dd = dict(e._data)
    del dd['_id']
    print(json.dumps(dd, indent=2))

    #e = Location("657fcdf56c57c39868307d8b")

    exits_mod = list(dict(x) for x in e.exits)
    for ei,exit in enumerate(e.exits):
        enew = Location.new_from_description(exit['location_description'], exit['story_importance'])
        exits_mod[ei]['id'] = enew._id
    
    e.set('exits', exits_mod)