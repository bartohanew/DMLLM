from .common import *
from .DM import DM
from .entity import Entity

class Battle(DM):

    def __init__(self, battle_description):
        self.battle_description = battle_description
        self.generate_enemies()

    def generate_enemies(self, model=DEFAULT_MODEL):
        my_messages = []
        prompt1 = flatten_whitespace(f"""
            Your goal will be to set up for a tabletop RPG battle.
            You are to interpret the following description of the battle, and generate enemies for the battle.
        """)
        prompt2 = flatten_whitespace(f"""
            Your response should be a JSON list of dictionaries, each with the following keys:
                - name
                - description
                - stats
                                     
            For example:
            [
                {{"name": "Thwark", "description": "A goblin. A small, green creature.", "stats": {{"hp": 10, "ac": 15, "str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10}}}},
                {{"name": "Mannard", "description": "A goblin. A small, green creature", "stats": {{"hp": 10, "ac": 15, "str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10}}}},
            ]
        """)
        prompt3 = flatten_whitespace(f"""
            The battle description is:
            {indent(self.battle_description, 2)}
        """)
        
        my_messages.append({'role': 'system', 'content': prompt1})
        my_messages.append({'role': 'system', 'content': prompt2})
        my_messages.append({'role': 'user', 'content': prompt3})

        enemy_json = self.json_retry_loop(my_messages, model=model)
        self.enemies = [
            Entity.fr(**enemy)
            for enemy in enemy_json
        ]
