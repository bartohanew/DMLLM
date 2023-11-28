from common import *

with open('characteristics_wizard.txt', 'r') as file:
    characteristics_wizard = file.read()

with open('how_to_dm.txt', 'r') as file:
    how_to_dm = file.read()

with open('story/adventure_hook.txt', 'r') as file:
    adventure_hook = file.read()

with open('story/backstory.txt', 'r') as file:
    backstory = file.read()

with open('story/overview.txt', 'r') as file:
    overview = file.read()

sys_message = f"""
{characteristics_wizard}
{how_to_dm}
{backstory}
{adventure_hook}
{overview}

You are to interpret the actions this wizard would take and answer quetions based on the information provided
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