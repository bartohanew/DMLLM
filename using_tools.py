from common import *

client = OpenAI()

type_modifiers = {
    'strength': 2,
    'dexterity': 1,
    'constitution': 0,
    'intelligence': -1,
    'wisdom': -2,
    'charisma': -3,
}
def roll_die(n_sides, type=None):
    import random
    result = random.randint(1, n_sides)
    if type is not None:
        result += type_modifiers[type]
    return result

roll_die_definition = {
    "name": "roll_die",
    "description": f"""Use the descriptions of the ability scores and their associated skills in the rulebook to help you decide what kind of ability check to use. Then determine how hard
the task is so that you can set the DC for the check. The higher the DC, the more difficult the task. The easiest way to set a DC is to decide whether the task's difficulty is easy, moderate, or hard, and use these three DCs:
+ Easy (DC 10). An easy task requires a minimal level of competence or a modicum of luck to accomplish. Moderate (DC 15). A moderate task requires a slightly higher level of competence to accomplish. A character with a combination of natural aptitude and specialized training can accomplish a moderate task more often than not.
+ Hard (DC 20). Hard tasks include any effort that is beyond the capabilities of most people without aid or exceptional ability. Even with aptitude and training, a character needs some amount of luck - or a lot of specialized training - to pull off a hard task.
""",
    "parameters": {
        "type": "object",
        "properties": {
            "n_sides": {
                "type": "integer",
                "description": "The number of sides on the die."
            },
            "type": {
                "type": "string",
                "description": "The type of die to roll. For example, 'strength' or 'dexterity'."
            }
        },
        "required": ["n_sides"]
    }
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

spell_lookup_definition = {
    "name": "spell_lookup",
    "description": f"Search a spell by name.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the spell."
            }
        },
        "required": ["name"]
    }
}

assistant = client.beta.assistants.create(
    name="DM Joe",
    instructions="You are a Dungeon Master. Use the provided functions to properly conduct your duties.",
    tools=[
        {"type" : "function",
         "function" : roll_die_definition
        },
        {"type" : "function",
         "function" : spell_lookup_definition
        },
    ],
    model="gpt-3.5-turbo",
)

assistant_id = assistant.id

print(f"Assistant ID: {assistant_id}")

import time

def wait_for_run_completion(thread_id, run_id):
    while True:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print(f"Current run status: {run.status}")
        if run.status in ['completed', 'failed', 'requires_action']:
            return run
        
import json

def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = tool.function.arguments

        if function_name == "roll_die":
            print("Rolling...")
            output = roll_die(**json.loads(function_args))

        elif function_name == "spell_lookup":
            print("Searching...")
            output = spell_lookup(**json.loads(function_args))

        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

    print(tool_output_array)

    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )

def print_messages_from_thread(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    for msg in messages:
        print(f"{msg.role}: {msg.content[0].text.value}")

thread = client.beta.threads.create()

def use_assistant(query):

  message = client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content=query,
  )

  print("Creating Assistant ")

  run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id,
  )

  print("Querying OpenAI Assistant Thread.")

  run = wait_for_run_completion(thread.id, run.id)

  if run.status == 'requires_action':
    run = submit_tool_outputs(thread.id, run.id, run.required_action.submit_tool_outputs.tool_calls)
    run = wait_for_run_completion(thread.id, run.id)

  print_messages_from_thread(thread.id)

use_assistant("I want to cast fireball.")

# i can cast spells and make ability checks