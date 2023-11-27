from common import *

with open('how_to_dm.txt', 'r') as file:
    how_to_dm = file.read()

sys_message = f"""
{how_to_dm}

You are to decide whether a roll is needed for the proposed action.
"""

M = [
    {"role": "system", "content": sys_message}, 
    {"role": "user", "content": "I want to attack the guard."}, # player says
]

r1 = get_response(M)
print(r1)