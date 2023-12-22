import logging
logger = logging.getLogger(__name__)

from .common import *
from .knowledge import Knowledge

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

            # in 'example', we should search for any lines which are JSON
            # and then we should add a 'type' field to the JSON
            elines = []
            for l in action['example'].splitlines():
                l = l.strip()
                if l.startswith("{"):
                    l = json.loads(l)
                    l['type'] = action['name']
                    elines.append(json.dumps(l))
                else:
                    elines.append(l)
            example = "\n".join(elines)

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
            *self.session.M,
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
            *self.session.M,
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
                logger.log(logging.DEBUG, f"Invalid JSON: {part}")

    def act_on(self, action):
        logger.log(logging.DEBUG, f"Executing...\n{json.dumps(action, indent=2)}")
        act = dict(action)
        if 'type' not in act:
            self.session.computersay_self("No type specified. Please rewrite this one.")
            return self.act()
        
        typ = action.pop('type')

        try:
            fn = getattr(self, typ)
            response = fn(**action)
            if response is not None:
                self.session.computersay_self(response)
            else:
                self.session.computersay_self("No response, action may have completed successfully.")
                print('Warning: no response from action', typ)

        except Exception as e:
            # first get the last line of the traceback
            tb = traceback.format_exc().splitlines()[-1]

            # then get the last line of the error
            error = str(e).splitlines()[-1]

            self.session.computersay_self(f"Error in command '{json.dumps(act, indent=2)}': {error} ({tb})")
            self.session.computersay_self("Please rewrite this one.")
            return self.act()

    def respond(self):

        my_messages = []
        prompt = f"""
        You are taking on the role of DM
        The message you type will be sent to the player from the DM.
        """
        
        my_messages.append({'role': 'system', 'content': prompt})

        if hasattr(self, 'additional_prompt'):
            my_messages.append({'role': 'system', 'content': self.additional_prompt()})

        response = get_response(my_messages + self.session.M, model=DEFAULT_MODEL)

        self.session.computersay(response)

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
        from .entity import Entity

        super().__init__(session)

        player = Entity(self.session.player_id)

        # if there is only one session, it's the new one we just made
        if self.session.previous is None:
            # ask if they want to start a new adventure
            qa = InfoGetter(self.session, {
                "name": "Get their real name, not the in-game name.",
                "adventure_description": "Get an idea of the kind of adventure the person would like"
            })
            qa.loop()
            player.set('real_name', qa['name'])
            
            self.session.computersay("Thank you for your answers. Give me a little while to generate the adventure for you.")
            self.adventure = Quest.new_from_description(qa['adventure_description'])

            # describe briefly the setting of the adventure
            self.session.computersay(f"Welcome to {self.adventure.name}!")

            # gather player information
            from .entity import Entity
            qa = InfoGetter(self.session, {
                "name": "Ask for a name for the player's character (in-game name).",
                "appearance": "The player's character's appearance. Be succinct.",
                "languages": "Languages which the player's character speaks.",
                "personality": "The player's character's personality. What are they like? Specific ticks?",
                "backstory": "The player's character's backstory. What specific events have shaped their life?",
                "goal": "A long-term life goal which is the focus of their attention.",
                "fears": "The player's character's fears. What are they afraid of?",
                "alignment": "The player's character's alignment. This is a moral compass, which can be one of the following: lawful good, neutral good, chaotic good, lawful neutral, neutral, chaotic neutral, lawful evil, neutral evil, chaotic evil.",
            })
            qa.loop()

            # set these attributes on the player
            for k,v in qa._info.items():
                player.set(k, v)

            player.query('brief_description')

            self.session.computersay(f"Let's begin!")
            self.session.set('location', self.adventure.start_location)
            self.session.set('quest', self.adventure._id)

        else:
            # otherwise we should extract some stuff from the previous session
            prev = self.session.previous
            self.session.set('location', prev.location)

            if not hasattr(prev, 'summary'):
                prev.set('summary', prev.summarize())
            s = prev.summary

            self.session.computersay_self("\nHere's a summary of the previous adventure:\n"+s)

            # find any extra messages, and we'll bring them into this session
            last_summ_dt = db.summaries.find({'player_id': self.session.player_id}).sort('end', -1).limit(1)
            last_summ_dt = list(last_summ_dt)[0]['end']
            uncounted_messages = db.messages.find({'player_id': self.session.player_id, 'created_at': {'$gt': last_summ_dt}})
            self.session.M += list(uncounted_messages)
            self.session.consolidate_messages()

        # and start the freeform adventure
        lesgo = FreeForm(self.session)
        lesgo.loop()

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
        p = (
            "The DM is here responsible for asking the player for the following bits of information, so we can move on with the game...\n"
            "Please only ask one question at a time and be brief.\n"
            "Don't be afraid to ask the player to elaborate, or to ask follow-up questions.\n"
            "Don't fill in any blanks for the player (unless they ask for it). Their answers should come from their messages.\n"
        )
        parts = [f"{k}: {v}" for k,v in self._target.items()]
        p += indent("\n".join(parts), 2)
        return p

    @action(
        description="set the value of one of the variables of interest",
        example="""{ "key": "key_of_interest", "value": "what you believe to be a true answer to the query" }""",
    )
    def set(self, key, value):
        self._info[key] = value
        return f"Set {key} to {value} successfully."

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
        example="""{ "action": "add|remove", "object": "detailed description of object", "quantity": 3 }""",
    )
    def inventory(self, action, object, quantity):
        if action == 'add':
            return self.session.player.add_inventory(object, quantity)
        elif action == 'remove':
            return self.session.player.remove_inventory(object, quantity)
    
    @action(
        description="Change the scene. Whenever you move to a different location, you should call this function.",
        example=(
            """{ "mode": "existing", "to": "name of valid exit" }\n"""
            """OR\n{ "mode": "new", "location_name": "name of new location", "location_description": "description of new location", "story_importance": "how does this location tie in to the story?" }\n"""
        )
    )
    def change_scene(self, mode, to=None, location_name=None, location_description=None, story_importance=None):
        
        if mode == "existing":
            from .location import Location
            loc = Location(self.session.location)
            exits = loc.exits
            for exit in exits:
                if exit['location_name'] == to:
                    # we need to generate even more information about this location
                    if 'location_id' not in exit:
                        loc = Location.new_from_description(
                            exit['location_description'], 
                            exit['story_importance'], 
                            synchronous=False,
                            expand=False
                        )
                        exit['location_id'] = loc._id
                        db.location.update_one(
                            {'_id': self.session.location},
                            {'$set': {'exits': exits}}
                        )

                    self.session.set('location', exit['location_id'])
                    return f"Changed scene to '{to}'"
                
            return f"Could not find exit '{to}'"
        
        elif mode == "new":
            from .location import Location
            loc = Location.new_from_description(location_description, story_importance)
            self.session.set('location', loc._id)
            return f"Changed scene to a completely new place: '{location_name}'"
        
        else:
            return f"Invalid mode {mode}"
    
    @action(
        description="roll dice to determine the outcome of an action",
        example="""{ "n_sides": 20, "n_dice": 1, "kind": "dexterity" }""",
    )
    def roll_dice(self, n_sides, n_dice, kind=None):
        import random
        result = [ random.randint(1, n_sides) for i in range(n_dice) ]
        result = result_og = sum(result)
        mod = 0
        if kind is not None and kind in self.type_modifiers:
            mod += self.session.player.type_modifiers[kind]
        result += mod

        return f"Rolled {n_dice}d{n_sides} (kind={kind}) {result_og} + {mod} = {result}"
    
    def additional_prompt(self):
        from .location import Location
        from .entity import Entity

        loc = Location(self.session.location)
        player = Entity(self.session.player_id)

        exit_str = "\n".join([f"NAME:{x['location_name']}\nDESCRIPTION:\n{x['location_description']}\nSTORY_IMPORTANCE:\n{x['story_importance']}\n" for x in loc.exits])

        p = (
            f"The player is right now in {loc.name}. Here's a description of this location:\n" +
            indent(loc.description, 2) + 
            "\n\nThe player has the following inventory:\n" +
            indent(player.get_inventory(), 2) +
            "\n\nThe places the player could go from here are as follows:\n" +
            indent(exit_str, 2)
        )
        #print(p)
        return p
    

if __name__ == "__main__":
    setup_logging()
    enable_logging_for_submodules(['knowledge'], level=logging.DEBUG)

    if False:
        for dbname in ['entity', 'location', 'session', 'messages', 'player', 'location', 'quest', 'subquest']:
            db[dbname].drop()

    import sys
    from .entity import Entity
    from .session import Session
    player = Entity("6584a773b2297e5345d4c461")
    #player = Entity.new()
    session = Session.new_with_player(player)
    dm = EntryDM(session)