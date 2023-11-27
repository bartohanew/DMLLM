from common import *

M = [
    {"role": "system", "content": "You are an advanced AI DM. Make a fun adventure"}, # computer says to itself
    {"role": "assistant", "content": "I am a wizard named Merlin. I am here to give you a quest."}, # computer says
    {"role": "user", "content": "I am a fighter named Grog. I am looking for a quest"}, # player says
]

r1 = get_response(M)
print(r1)

r2 = get_response([
    {"role": "system", "content": "You just said: " + r1}, 
    {"role": "system", "content": "Extract the meaningful items of lore which are introduced in this description."}, # computer says to itself
])
print("\n\n\n") # make 3 spaces between the last and the most recent
print(r2)