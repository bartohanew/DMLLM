from tools import *
info = """
The current state of the world is:
+ There are three players: Alice, Bob, and Charlie.
+ Alice
    + 10 hit points
    + human wizard
    + can cast fireball, magic missile, and shield
    + has a dagger
    + has a spellbook
+ Bob
    + 10 hit points
    + human fighter
    + has a sword
+ Charlie
    + 10 hit points
    + human cleric
    + can cast cure wounds
    + has a mace
+ There are three monsters: a goblin, an orc, and a troll.
+ goblin
    + 3 hit points
    + 70 ft from Alice, 100ft from Bob, 50ft from Charlie
+ orc
    + 6 hit points
    + 50 ft from Alice, 30ft from Bob, 100ft from Charlie
+ troll
    + 10 hit points
    + 100 ft from Alice, 50ft from Bob, 30ft from Charlie
"""

t = Thread()

a = t.create_assistant(
    name="DM Joe",
    instructions="You are a Dungeon Master. Use the provided functions to properly conduct your duties.",
)

def roll_die(n_sides, n_dice, type=None):
    import random
    result = [ random.randint(1, n_sides) for i in range(n_dice) ]
    result = sum(result)
    if type is not None and type in type_modifiers:
        result += type_modifiers[type]
    return result

a.add_tool(
    name="roll_die",
    description=f"""
        Use the descriptions of the ability scores and their associated skills in the rulebook to help you decide what kind of ability check to use. Then determine how hard
        the task is so that you can set the DC for the check. The higher the DC, the more difficult the task. The easiest way to set a DC is to decide whether the task's difficulty is easy, moderate, or hard, and use these three DCs:
        + Easy (DC 10). An easy task requires a minimal level of competence or a modicum of luck to accomplish. Moderate (DC 15). A moderate task requires a slightly higher level of competence to accomplish. A character with a combination of natural aptitude and specialized training can accomplish a moderate task more often than not.
        + Hard (DC 20). Hard tasks include any effort that is beyond the capabilities of most people without aid or exceptional ability. Even with aptitude and training, a character needs some amount of luck - or a lot of specialized training - to pull off a hard task.  
    """,
    parameters=(
        Parameters()
            .add_property("n_sides", "integer", "The number of sides on the die.", required=True)
            .add_property("n_dice", "integer", "The number of dice to roll.", required=True)
            .add_property("type", "string", "The ONLY options are strength, dexterity, constitution, intelligence, wisdom, charisma, and attack.")
    ).json(),
    function=roll_die,
)

type_modifiers = {
    'strength': 2,
    'dexterity': 1,
    'constitution': 0,
    'intelligence': -1,
    'wisdom': -2,
    'charisma': -3,
}

def spell_lookup(name):
    print('searching for spell', name)

    import requests
    nameq = name.strip().replace(' ', '+')
    url = f"https://www.dnd5eapi.co/api/spells/?name={nameq}"
    response = requests.get(url)
    response = response.json()

    full = []
    for result in response['results']:
        url = result['url']
        response = requests.get(f"https://www.dnd5eapi.co{url}")
        full.append(response.json())

    if not len(full):
        return "No spells found."

    return json.dumps(full, indent=2)

a.add_tool(
    name="spell_lookup",
    description=f"""
        Search the D&D 5e API for a spell.
    """,
    parameters=(
        Parameters()
            .add_property("name", "string", "The name of the spell you'd like to look up.", required=True)
    ).json(),
    function=spell_lookup,
)

# now let's begin!
a.initialize()
t.say("user", info)
t.say("user", "I cast fireball on the goblin.")
print(a.complete())