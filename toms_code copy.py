from common import *

with open('characteristics_wizard.txt', 'r') as file:
    characteristics_wizard = file.read()

with open('how_to_dm.txt', 'r') as file:
    how_to_dm = file.read()

with open('story/adventure_hook.txt', 'r') as file:
    adventure_hook = file.read()

with open('story/backstory.txt', 'r') as file:
    backstory = file.read()

with open('story/part_1.txt', 'r') as file:
    part_1 = file.read()

sys_message = f"""
{characteristics_wizard}
{how_to_dm}
{backstory}
{adventure_hook}
{part_1}

You are to interpret the actions this wizard would take and answer quetions based on the information provided.
After two inputs by the player, continue with the goblin_ambush.txt file
"""

M = [
    {"role": "system", "content": sys_message}, 
]

while True:
    m = input(">")
    M.append({"role": "user", "content": m})
    r1 = get_response(M)
    print(r1)
    M.append({"role": "assistant", "content": r1})