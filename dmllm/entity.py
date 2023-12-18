from .common import *
from .knowledge import Knowledge

class Entity(Knowledge):
    questions = {
        "name": "What is the character's name? Please just give the name, no description or thought process.",
        "appearance": "Describe the character's appearance. Be succinct.",
        "languages": "What languages does the character speak? Simply list the languages.",
        "personality": "Describe the character's personality. What are they like? Specific ticks?",
        "backstory": "Describe the character's backstory. Invent specific events that has shaped their life.",
        "goal": "What are the character's goal right now? Give one long-term life goal which is the focus of their attention.",
        "fears": "What are the character's fears? What are they afraid of?",
        "brief_description": "Give a brief description of the character. This should be a single sentence, summarizing the character.",
    }

    attribute_prompt = flatten_whitespace(f"""
        Your role in life is to imagine the world of a character, in a tabletop RPG.
        You are to expand the description of a new character you are building, to respond to specific questions about the character.
        Be specific and imaginative. Try to weave the character into the world of the adventure.
        You must be capable of building flawed, evil, heartless, naive, and otherwise extremely imperfect characters.
        Don't be afraid to not paint any silver linings.
        Try to be brief, but not too brief. Concise.
    """)

    @classmethod
    def new_from_description(cls, description, alignment=None):

        knowledge_type = cls.__name__.lower()
        cid = db[knowledge_type].insert_one({}).inserted_id
        c = cls(cid)
        c.set('description', description)

        if alignment is None:
            from random import choice
            alignment = choice(['lawful good', 'neutral good', 'chaotic good', 'lawful neutral', 'neutral', 'chaotic neutral', 'lawful evil', 'neutral evil', 'chaotic evil'])
        c.set('alignment', alignment)

        for q in cls.questions:
            c.query(q)

        return c

    def add_inventory(self, item, quantity=1):
        self._data['inventory'].append(item)
        db.characters.update_one({'_id': self._id}, {'$set': {'inventory': self._data['inventory']}})

    def remove_inventory(self, item):
        self._data['inventory'].remove(item)
        db.characters.update_one({'_id': self._id}, {'$set': {'inventory': self._data['inventory']}})

    def get_inventory(self):
        inventory = self.get_txt("inventory")
        if inventory is None:
            if self.story_part_name == 'start':
                self.add_inventory("10 gold pieces")
                self.add_inventory("a backpack")
                self.add_inventory("a bedroll")
                self.add_inventory("a mess kit")
                self.add_inventory("a tinderbox")
                self.add_inventory("10 torches")
                self.add_inventory("10 days of rations")
                self.add_inventory("a waterskin")
                self.add_inventory("50 feet of hempen rope")
                return self.get_inventory()
            else:
                inventory = "The player has nothing."

        return inventory

if __name__ == "__main__":
    import sys
    e = Entity.new_from_description(sys.argv[1], alignment=sys.argv[2])
    print(e)
    dd = dict(e._data)
    del dd['_id']
    print(json.dumps(dd, indent=2))