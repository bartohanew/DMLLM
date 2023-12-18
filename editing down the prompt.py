from common import *

with open('story/adventure_hook.txt', 'r') as file:
    adventure_hook = file.read()

with open('story/backstory.txt', 'r') as file:
    backstory = file.read()

with open('story/part_1.txt', 'r') as file:
    part_1 = file.read()

with open('characteristics_wizard.txt', 'r') as file:
    characteristics_wizard = file.read()

with open('story/goblin_ambush.txt', 'r') as file:
    goblin_ambush = file.read()

sys_message = f"""
{backstory}
{adventure_hook}
{part_1}
{characteristics_wizard}
{goblin_ambush}

You play the role of the dungeon master aka dm
I play the role of a player, not a dungeon master
The characters are controlled by the player and you are not a player
The player is a wizard and you are to use the information provided to answer questions the player may have
Use the information provided to answer and questions the player may have
Ability scores and skills are found in the ab_scores.txt file. Please refer to this file whenever a roll is necessary
It is up to you to make the roll, add the appropriate modifier, and tell me the result. Do not ask me to make a roll

The wizard's ability scores are as follows: 
**Strength** = 10 
**Dexterity** = 15 
**Constitution** = 14 
**Intelligence** = 16 
**Wisdom** = 12 
**Charisma** = 8
"""

M = [
    {"role": "system", "content": sys_message}, 
]

while True:
    m = input(">")
    M.append({"role": "user", "content": m})
    r1 = get_response(M)
    print("\n\n\n")
    print(r1)
    M.append({"role": "assistant", "content": r1})