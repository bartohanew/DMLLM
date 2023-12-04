from modularity import *

t = Thread()

a = t.create_assistant(
    name="Friendly Bot",
    instructions="""
        You are my friend. Ask me about myself and remember what I say. 
        Whenever I say something you didn't know, add it to your diary.
        Whenever you want to see if you know something, ask me.
    """,
    model="gpt-4-1106-preview"
)

def add_information(something):
    with open("running text diary.txt", "a") as f:
        f.write(something + "\n")

    return "Successfully saved the information."

a.add_tool(
    name="save_something",
    description=f"""
        You have a text file diary that you can save information to.
        Just say what you want to remember and I will add it to the file.
        Each sentence should be on its own line.
    """,
    parameters=(
        Parameters()
            .add_property("something", "string", "The information to save.", required=True)
    ).json(),
    function=add_information,
)

def remember_information(search_term):
    results = []

    with open("running text diary.txt", "r") as f:
        all_info = f.read()
        for line in all_info.split('\n'):
            if search_term in line:
                results.append(line)

    if not len(results):
        return "No results found."

    return '\n'.join(results)


a.add_tool(
    name="remember_something",
    description=f"""
        You have a text file diary that you can remember information from.
        Search for a key term and I will return all the lines that contain that term.
    """,
    parameters=(
        Parameters()
            .add_property("search_term", "string", "The term to search for.", required=True)
    ).json(),
    function=remember_information,
)

# now let's begin!
a.initialize()

while True:
    prompt = input(">> ")
    t.say("user", prompt)
    a.complete()
    t.print_last_message()