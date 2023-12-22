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
        "alignment": "What is the character's alignment?",
        "roll_modifiers": (
            "What are the character's roll modifiers? This should be a JSON object, with keys being the roll type, and values being the modifier.\n"
            "Please always include the following keys: strength, dexterity, constitution, intelligence, wisdom, charisma."
        ),
    }

    attribute_prompt = flatten_whitespace(f"""
        Your role in life is to imagine the world of a character, in a tabletop RPG.
        You are to expand the description of a new character you are building, to respond to specific questions about the character.
        Be specific and imaginative. Try to weave the character into the world of the adventure.
        You must be capable of building flawed, evil, heartless, naive, and otherwise extremely imperfect characters.
        Don't be afraid to not paint any silver linings.
        Try to be brief, but not too brief. Concise.
    """)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data['inventory'] = self._data.get('inventory', {})

    @classmethod
    def new_from_description(cls, description, alignment=None, synchronous=True):

        knowledge_type = cls.__name__.lower()
        cid = db[knowledge_type].insert_one({}).inserted_id
        c = cls(cid)
        c.set('description', description)

        if alignment is None:
            from random import choice
            alignment = choice(['lawful good', 'neutral good', 'chaotic good', 'lawful neutral', 'neutral', 'chaotic neutral', 'lawful evil', 'neutral evil', 'chaotic evil'])
        c.set('alignment', alignment)

        for q in cls.questions:
            c.query(q, synchronous=synchronous)

        return c
    
    def _update_inventory(self):
        db.entity.update_one({'_id': self._id}, {'$set': {'inventory': self._data['inventory']}})

    def add_inventory(self, item, quantity=1):
        if item in self._data['inventory']:
            self._data['inventory'][item] += quantity
        else:
            self._data['inventory'][item] = quantity

        self._update_inventory()
        return f"The player now has {self._data['inventory'][item]}X '{item}'."

    def remove_inventory(self, item, quantity=1):
        if item in self._data['inventory']:
            self._data['inventory'][item] -= quantity
            if self._data['inventory'][item] <= 0:
                del self._data['inventory'][item]
            
            self._update_inventory()
            return f"The player now has {self._data['inventory'][item]}X '{item}'."
        else:
            return f"The player does not have {item}."
        
    def get_inventory(self):
        inventory = self._data['inventory']
        if not len(inventory):
            return "The player has nothing."
        
        inventory_str = []
        for k,v in inventory.items():
            inventory_str.append(f"{v}x {k}")
        inventory_str = "\n".join(inventory_str)
        return inventory_str

if __name__ == "__main__":
    import sys
    e = Entity.new_from_description(sys.argv[1], alignment=sys.argv[2])
    print(e)
    dd = dict(e._data)
    del dd['_id']
    print(json.dumps(dd, indent=2))