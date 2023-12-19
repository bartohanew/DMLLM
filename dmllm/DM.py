from .common import *
from .knowledge import Knowledge

adventure_name = "alec_first"
# find the last summary of the state the game was left in
#model = "gpt-3.5-turbo"
model = "gpt-4-1106-preview"

class Session(Knowledge):
    def __init__(self, _id):
        super().__init__(_id)
        
        # get the messages
        self.M = self.messages()

    @classmethod
    def new_with_player(self, player):
        session = Session.new()
        session.set('player_id', player._id)
        return session

    def messages(self, limit=None):
        # sorted by dt, ascending, with the last message always the most recent
        ms = db.messages.find({'session_id': self._id}).sort('dt', -1)
        if limit is not None:
            ms = ms.limit(limit)
        return list(ms)

    def _summarize_block(self, messages):
        message_text = "\n".join([f"+ {x['role']}: {x['content']}" for x in messages])
        prompt = f"""
        Your goal is to summarize the plotpoints contained in the following conversation between a DM and a player.
        In each plot point, be as specific as possible.
        Keep note of any characters, locations, or items that are mentioned.
        Do not include any information not present in the following messages!

        Messages:
        {message_text}
        """

        messages = [
            {"role": "system", "content": prompt},
        ]

        response = get_response(messages)
        return response

    def summarize(self):
        # loop, adding messages until doing so would put us over the character limit,
        # summarizing at each step
        this_block = []
        summaries = []
        char_limit = 4500

        for m in self.messages():
            current_len = len("\n".join(this_block))
            this_chunk = f"{m['role']}\n{m['content']}\n"
            if current_len + len(this_chunk) + 1 > char_limit:
                summaries.append(self._summarize_block(this_block))
                this_block = []

            this_block.append(this_chunk)

        summaries.append(self._summarize_block(this_block))

        if len(summaries) > 1:
            return self._summarize_block(summaries)
        
        return summaries[0]

    # ------------------
    # SAYING STUFF
    # ------------------

    def humansay(self, content):
        self.M.append({"role": "user", "content": content})
        db.messages.insert_one({
            'session_id': self._id,
            'role': 'user',
            'content': content,
            'dt': dt.datetime.utcnow(),
        })

    def computersay(self, content):
        self.M.append({"role": "assistant", "content": content})
        db.messages.insert_one({
            'session_id': self._id,
            'role': 'assistant',
            'content': content,
            'dt': dt.datetime.utcnow(),
        })
        print(content)

    def computersay_self(self, content):
        self.M.append({"role": "system", "content": content})
        db.messages.insert_one({
            'session_id': self._id,
            'role': 'system',
            'content': content,
            'dt': dt.datetime.utcnow(),
        })

# we need a decorator for actions
def action(description, example, **kwargs):
    def decorator(fn):
        fn._is_action = True
        fn._info = {
            'description': description,
            'example': example,
            **kwargs,
        }
        return fn
    return decorator



class DM:

    def __init__(self, session):
        self.session = session
        self.actions = self._gather_actions()

        previous_sessions = db.sessions.find({'player_id': self.session.player_id}).sort('dt', -1).limit(2)
        previous_sessions = list(previous_sessions)[1:]
        if len(previous_sessions) == 0:
            self.last_session = None
        else:
            self.last_session = previous_sessions[0]

        self.M = []

    def _gather_actions(self):
        """
        Decorators tag any class function as an action with an attribute _is_action, set to True.
        This will also have an _info attribute, a dictionary which contains the description and example of the action, and any other args passed to the decorator.
        Let's just return the information, adding the function to the dictionary.
        """

        from inspect import getmembers, ismethod

        actions = {}
        for name, fn in getmembers(self):
            if ismethod(fn) and getattr(fn, '_is_action', False):
                actions[name] = fn._info
                actions[name]['fn'] = fn
                actions[name]['name'] = name

        actions = [
            actions[x] for x in sorted(actions.keys())
        ]

        return actions

    def _format_actions(self):
        """
        description: a description of the action. will be given as "If you want to {description}, type:"
        example: an example of a properly formed action, with all the relevant arguments
        """

        parts = []
        for action in self.actions:
            parts.append(f"{action['name']}: {action['description']}")
            example = json.loads(action['example'])
            example['type'] = action['name']

            parts.append((
                f"If you want to {action['description']}, type:"
                f"\n{json.dumps(example)}"
            ))

        return "\n\n".join(parts)

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

        response = get_response(messages, model=DEFAULT_MODEL)

        self.session.computersay_self("(thinking...) " + response)

    def act(self):
        actions = self._format_actions()
        action_names = [x['name'] for x in self.actions]
        if len(action_names) == 1:
            action_names_str = action_names[0]
        else:
            action_names_str = ", ".join(action_names[:-1]) + ", or " + action_names[-1]

        prompt = f"""        
            Based on the dialogue so far, you are to decide what actions to take next.
            Most of the time no action will need to be taken. In this case, simply type "pass".
            Please do not act in a way not directly implied by the dialogue so far.
            Although there is no rush to change the 'scene', you must eventually do so, in order to continue the story.

            {actions}

            ALWAYS USE DOUBLE QUOTES FOR JSON STRINGS

            You can type a command on each line.
            You CANNOT mix commands and statements.
        """

        messages = [{"role": "system", "content": prompt}]
        
        if hasattr(self, 'additional_prompt'):
            messages.append({'role': 'system', 'content': self.additional_prompt()})
        
        messages += [
            *self.M,
            {"role": "system", "content": f"What do you do? (type = {action_names_str}). Use only JSON strings, one per line. If no action need be taken from the most recent message, simply type 'pass'."},
        ]

        response = get_response(messages, model=DEFAULT_MODEL)
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
            self.session.computersay_self(response)
        except Exception as e:
            # first get the last line of the traceback
            tb = traceback.format_exc().splitlines()[-1]

            # then get the last line of the error
            error = str(e).splitlines()[-1]

            self.session.computersay_self(f"Error in command '{json.dumps(act, indent=2)}': {error} ({tb})")
            self.session.computersay_self("Please rewrite this one.")
            self.act()

    def respond(self):

        my_messages = []
        prompt = f"""
        You are taking on the role of DM
        The message you type will be sent to the player from the DM.
        """
        
        my_messages.append({'role': 'system', 'content': prompt})

        if hasattr(self, 'additional_prompt'):
            my_messages.append({'role': 'system', 'content': self.additional_prompt()})

        response = get_response(my_messages + self.M, model=DEFAULT_MODEL)

        self.session.computersay(response)

    def consolidate_messages(self):
        # remember a summary of the messages
        self.summary.append(self.summarize_plotline())

        # (mostly) clear the messages
        self.M = self.M[-2:]

    # ------------------
    # Running the Conversation
    # ------------------

    def exchange(self):
        
        # human does its thing
        query = input(">> ")
        self.session.humansay(query)

        # computer does its thing
        self.act()
        self.think()
        self.respond()
        self.act()

    def loop(self):
        while True:
            self.exchange()


class EntryDM(DM):

    def __init__(self, session):
        from .story_alec import Quest
        super().__init__(session)

        # if there is only one session, it's the new one we just made
        if self.last_session is None:
            # ask if they want to start a new adventure
            qa = InfoGetter(self.session, {
                "name": "Get their real name, not the in-game name.",
                "adventure_description": "Get an idea of the kind of adventure the person would like"
            })
            qa.loop()
            self.adventure = Quest.new_from_description(qa['adventure_description'])

        else:
            # otherwise we should extract some stuff from the previous session
            self.location = self.last_session.get('location', None)

class InfoGetter(DM):
    def __init__(self, session, *args, **kwargs):
        self._info = {}

        self.session = session

        if len(args) == 1:
            self._target = args[0]
        elif len(args) == 0 and len(kwargs):
            self._target = kwargs

        super().__init__(session)

    def additional_prompt(self):
        p = "The DM is here responsible for asking the player for the following bits of information, so we can move on with the game...\nPlease only ask one question at a time and be brief.\n"
        parts = [f"{k}: {v}" for k,v in self._target.items()]
        p += indent("\n".join(parts), 2)
        return p

    @action(
        description="set the value of one of the variables of interest",
        example="""{ "key": "key_of_interest", "value": "what you believe to be a true answer to the query" }""",
    )
    def set(self, key, value):
        self._info[key] = value

    # getting like a dictionary
    def __getitem__(self, k):
        return self._info[k]

    def exchange(self):

        # computer does its thing
        self.respond()

        # human does its thing
        query = input(">> ")
        self.session.humansay(query)

        self.act()

    def loop(self):
        while True:
            self.exchange()

            if set(self._target) <= set(self._info):
                break
    
class FreeForm(DM):
    @action(
        description="add an item to the inventory",
        example="""{ "type": "inventory", "action": "add|remove", "object": "detailed description of object" }""",
    )
    def inventory(self, action, object):
        self.add_txt("inventory", f"{action}: {object}")
        return f"Inventory {action}: {object}"
    
    @action(
        description="change the scene",
        example="""{ "type": "change_scene", "to": "start" }""",
    )
    def change_scene(self, to):
        self.story_part_name = to
        self.set_txt("story_part", self.story_part_name)

        return "Changed scene to " + to
    
    @action(
        description="roll hit dice",
        example="""{ "type": "roll_hit_dice", "n_sides": 6, "n_dice": 2, "kind": "dexterity" }""",
    )
    def roll_hit_dice(self, n_sides, n_dice, kind=None, **kwargs):
        import random
        result = [ random.randint(1, n_sides) for i in range(n_dice) ]
        result = result_og = sum(result)
        mod = 0
        if kind is not None and kind in self.type_modifiers:
            mod += self.type_modifiers[kind]
        result += mod

        return f"Rolled {n_dice}d{n_sides} (kind={kind}) {result_og} + {mod} = {result}"
    

if __name__ == "__main__":
    import sys
    from .player import Player
    player = Player.new()
    session = Session.new_with_player(player)
    dm = EntryDM(session)
    print(dm._format_actions())
    dm.loop()