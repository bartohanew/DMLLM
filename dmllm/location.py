from .common import *
from .knowledge import Knowledge

class Location(Knowledge):
    questions = {
        "name": "Give a short name for this location.",
        "description": "Describe the location. What does it look like? What is it like to be there? What is the atmosphere?",
        "exits": (
            "What exits are there from this location?\n"
            "Your response should be a list of JSON objects which each represent a place you can go from here.\n"
            "Each JSON object should have the following keys: location_name, location_description, obstacles, story_importance."
        )
    }

    attribute_prompt = flatten_whitespace(f"""
        Your role in life is to imagine a location, in a tabletop RPG.
    """)

    @classmethod
    def new_from_description(cls, description, story_importance=None, synchronous=True, expand=True):

        knowledge_type = cls.__name__.lower()
        cid = db[knowledge_type].insert_one({}).inserted_id
        c = cls(cid)
        c.set('description', str(description))
        if story_importance is not None:
            c.set('story_importance', str(story_importance))

        for q in cls.questions:
            c.query(q, synchronous=expand or synchronous)

        if expand:
            if type(c.exits) == str:
                return c
            
            exits_mod = list(dict(x) for x in c.exits)
            for ei,exit in enumerate(c.exits):
                enew = Location.new_from_description(exit['location_description'], exit['story_importance'], synchronous=False, expand=False)
                exits_mod[ei]['location_id'] = enew._id
            c.set('exits', exits_mod)

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