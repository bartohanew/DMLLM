import openai
from openai import OpenAI

# set API KEY
client = OpenAI(api_key = "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")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages = [
        {"role": "system", "content": "You are an advanced AI DM. Make a fun adventure"},
        {"role": "user", "content": "I am a fighter named Grog. I am looking for a quest"},
    ],
    max_tokens=None,
    temperature=0.9,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.6,
    #stop=["\n"],
)

print(response)