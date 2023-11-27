from common import *

with open('characteristics_wizard.txt', 'r') as file:
    characteristics_wizard = file.read()

sys_message = f"""
{characteristics_wizard}

You are to answer questions about the personality of a wizard based on the information found in the characteristics_wizard.txt file
"""

M = [
    {"role": "system", "content": sys_message}, 
    {"role": "user", "content": "what are my flaws?"}, # player says
]

r1 = get_response(M)
print(r1)