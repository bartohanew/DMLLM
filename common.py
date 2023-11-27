import openai
from openai import OpenAI

import os
from dotenv import load_dotenv
load_dotenv()

open_ai_key = os.getenv("OPENAI_API_KEY")

# set API KEY
client = OpenAI(api_key = open_ai_key)

def get_response(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = messages,
        max_tokens=500,
        temperature=0.9,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
    )

    return response.choices[0].message.content