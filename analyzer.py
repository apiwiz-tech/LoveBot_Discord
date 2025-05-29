import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

async def analyze_message(text: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Analyze emotional tone and personality traits."},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()

async def detect_argument_with_gpt(messages: list[str]) -> bool:
    conversation = '\n'.join(messages)
    prompt = (
        "You are a relationship AI. Given this conversation, "
        "determine if there is an argument or tension. Reply with YES or NO."
        f"\nConversation:\n{conversation}"
    )
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.choices[0].message.content.strip().upper()
    return answer == "YES"

async def generate_intervention_with_gpt(messages: list[str]) -> str:
    conversation = '\n'.join(messages)
    prompt = (
        "You are a compassionate AI relationship counselor. "
        "The following conversation has some tension. "
        "Provide a gentle, constructive message to help both people calm down and reflect."
        f"\nConversation:\n{conversation}"
    )
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()

async def explain_conflict_with_gpt(messages: list[str]) -> str:
    conversation = '\n'.join(messages)
    prompt = (
        "You are an expert relationship counselor AI. "
        "Analyze the following conversation and explain what the conflict is about. "
        "Give constructive advice on how to resolve it."
        f"\nConversation:\n{conversation}"
    )
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()

async def summarize_week(memory) -> str:
    msgs = memory.get_recent(days=7)
    content = '\n'.join(m.content for m in msgs)
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the key topics and emotions."},
            {"role": "user", "content": content},
        ],
    )
    return response.choices[0].message.content.strip()

async def highlight_sweet(memory) -> str:
    msgs = memory.get_all()
    content = '\n'.join(m.content for m in msgs)
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Identify the most affectionate and emotional messages."},
            {"role": "user", "content": content},
        ],
    )
    return response.choices[0].message.content.strip()
