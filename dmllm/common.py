from modularity import flatten_whitespace, indent
import json
from pymongo import MongoClient
from modularity import OpenAI
import traceback
import datetime as dt

db = MongoClient()['DMLLM']
openai = OpenAI()

DEFAULT_MODEL = "gpt-4-1106-preview"

def get_response(messages, model=DEFAULT_MODEL, **kwargs):
    kwargs = {
        'max_tokens': None,
        'temperature': 0.9,
        'top_p': 1,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.6,
        **kwargs,
    }

    response = openai.chat.completions.create(
        model=model,
        messages = messages,
        **kwargs,
    )

    return response.choices[0].message.content

def json_retry_loop(messages, model=DEFAULT_MODEL, loop_i=0):
    while True:
        response = get_response(messages, model=model)
        try:
            return json.loads(response)
        except json.decoder.JSONDecodeError:
            messages.append({'role': 'system', 'content': "Invalid JSON. Please try again."})

            loop_i += 1
            if loop_i > 3:
                raise
            
            return json_retry_loop(messages, model=model, loop_i=loop_i)
