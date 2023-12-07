from common import *
import json

adventure_name = "alec_first"

#model = "gpt-3.5-turbo"
model = "gpt-4-1106-preview"

from modularity import OpenAI
import traceback

client = OpenAI()

class Entity:
    def __init__(self, name, description, stats):
        self.name = name
        self.description = description
        self.stats = stats

    def __repr__(self):
        return f"Entity({self.name}, {self.description}, {self.stats})"

    def __str__(self):
        return f"Entity({self.name}, {self.description}, {self.stats})"

class Battle:

    def __init__(self, battle_description):
        self.battle_description = battle_description

    # ------------------
    # SAYING STUFF
    # ------------------

    def humansay(self, content):
        self.M.append({"role": "user", "content": content})
        self.add_txt("dialogue", f"Player:\n{content}")

    def computersay(self, content):
        self.M.append({"role": "assistant", "content": content})
        self.add_txt("dialogue", f"DM:\n{content}")
        print("DM:", content)

    def computersay_self(self, content):
        self.M.append({"role": "system", "content": content})
        self.add_txt("dialogue", f"DM (to themselves):\n{content}")

    # ------------------
    # Thinking, Acting, and Responding
    # ------------------

    def think(self):
        prompt = f"""
        You are an assistant to the DM.
        Speak directly to the DM (not the player).
        Give some thoughts or ideas to the DM to help them conduct their duties.
        If you think everything is clear, type 'pass'.
        Be concise, specific, and clear.
        """

        messages = [
            {"role": "system", "content": prompt},
            *self.M,
            {"role": "system", "content": "What do you think to yourself? Be brief."},
        ]

        response = get_response(messages, model=model)

        self.computersay_self("(thinking...) " + response)

    def act(self):
        story_part = self.story_part

        next_steps = "\n".join([f"\t{x}: {y}" for x, y in story_part['next_steps'].items()])
        inventory = self._format_inventory()
        prompt = f"""
            Your current inventory is:
            {inventory}
        
            Based on the dialogue so far, you are to decide what actions to take next.
            Most of the time no action will need to be taken. In this case, simply type "pass".
            Please do not act in a way not directly implied by the dialogue so far.
            Although there is no rush to change the 'scene', you must eventually do so, in order to continue the story.

            If you want to change the scene, type:
            {{"type": "change_scene", "to": "scene name"}}

            To roll hit dice, type:
            {{"type: "roll_hit_dice", "n_dice": 1, "n_sides": 6, "type": "strength"}}

            To add or remove from inventory, type:
            {{"type: "inventory", "action": "add|remove", "object": "object name, description, and/or stats"}}

            ALWAYS USE DOUBLE QUOTES FOR JSON STRINGS

            You can type a command on each line.
            You CANNOT mix commands and statements.

            Scenes available, their names and descriptions:
            {next_steps}
        """

        messages = [
            {"role": "system", "content": prompt},
            *self.M,
            {"role": "system", "content": "What do you do? (type = change_scene, roll_hit_dice, or inventory). Use only JSON strings, one per line. If no action need be taken from the most recent message, simply type 'pass'."},
        ]

        response = get_response(messages, model=model)
        if response.strip() == "pass":
            return

        parts = response.split("}")
        for part in parts:
            if part == "":
                continue
            part += "}"

            try:
                part = json.loads(part)
                self.act_on(part)
            except json.decoder.JSONDecodeError:
                print("Invalid JSON:", part)

    def act_on(self, action):
        print("Executing... ", json.dumps(action, indent=2))
        act = dict(action)
        typ = action.pop('type')

        try:
            fn = getattr(self, typ)
            response = fn(**action)
            self.computersay_self(response)
        except Exception as e:
            # first get the last line of the traceback
            tb = traceback.format_exc().splitlines()[-1]

            # then get the last line of the error
            error = str(e).splitlines()[-1]

            self.computersay_self(f"Error in command '{json.dumps(act, indent=2)}': {error} ({tb})")
            self.computersay_self("Please rewrite this one.")
            self.act()

    def respond(self):

        story_part = self.story_part

        my_messages = []
        inventory = self._format_inventory()
        prompt = f"""
        You are a DM. 
        You are currently in the scene "{story_part['name']}".

        Your current inventory is:
        {inventory}

        The message you type will be sent to the player from the DM.

        Description of the current scene:
            {story_part['description']}
        """
        
        my_messages.append({'role': 'system', 'content': prompt})

        response = get_response(my_messages + self.M, model=model)

        self.computersay(response)

        # consolidate things, if it's getting long
        if len(self.M) > 10:
            # remember a summary of the messages
            self.summary.append(self.summarize_plotline())

            # (mostly) clear the messages
            self.M = self.M[-2:]


    # ------------------
    # Running the Conversation
    # ------------------


    def run(self):
        
        # human does its thing
        query = input(">> ")
        self.humansay(query)

        # computer does its thing
        self.act()
        self.think()
        self.respond()
        self.act()

    def loop(self):
        while True:
            self.run()


c = Convo(adventure_name)
c.loop()