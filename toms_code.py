from common import *

with open('characteristics_wizard.txt', 'r') as file:
    characteristics_wizard = file.read()

sys_message = f"""
{characteristics_wizard}

You are to interpret the actions this wizard would take and answer quetions based on the information provided
"""

M = [
    {"role": "system", "content": sys_message}, 
    {"role": "user", "content": "what does galanodel translate to?"}, # player says
]

r1 = get_response(M)
print(r1)