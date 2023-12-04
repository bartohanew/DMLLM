from modularity import *

pieces_of_information = {
    "Alec-personality": """I use polysyllabic words that convey the 
    impression of erudition. Also, I’ve spent 
    so long in the temple that I have little 
    experience dealing with people on a 
    casual basis""",

    "Alec-ideals": """Knowledge. The path to power and self improvement is through knowledge""",

    "Alec-bonds": """The tome I carry with me is the record of 
    my life’s work so far, and no vault is secure
    enough to keep it safe.""",

    "Alec-flaws": """I’ll do just about anything to uncover 
    historical secrets that would add to 
    my research.""",
}

t = Thread()

a = t.create_assistant(
    name="DM Joe",
    instructions="You are a Dungeon Master. Use the provided functions to properly conduct your duties.",
)

def lookup_information(something):
    something = something.strip().lower()
    return pieces_of_information[something]

a.add_tool(
    name="lookup_information",
    description=f"""
        You are equipped with some information about the characters in the story. You can use this information to help you make decisions about how to proceed.
        The pieces of information you have access to is the following: {', '.join(pieces_of_information.keys())}
    """,
    parameters=(
        Parameters()
            .add_property("something", "string", "The name of the piece of information you want to look up.", required=True)
    ).json(),
    function=lookup_information,
)

# now let's begin!
a.initialize()

while True:
    prompt = input(">> ")
    t.say("user", prompt)
    a.complete()
    t.print_last_message()