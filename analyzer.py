### `analyzer.py`
python
import os
import openai

openai.api_key = os.getenv('OPENAI_KEY')

# Analyze tone, emotion, personality
def analyze_message(text):
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[{'role': 'system', 'content': 'Analyze emotional tone and personality traits.'},
                  {'role': 'user', 'content': text}]
    )
    return response.choices[0].message.content

# Simple argument detection (can be improved)
def detect_argument(text):
    triggers = ['you always', 'you never', 'stop', 'shut up', '?']
    return any(word in text.lower() for word in triggers)

# Summarize last week's messages
def summarize_week(memory):
    msgs = memory.get_recent(days=7)
    content = '\n'.join(m.content for m in msgs)
    resp = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[{'role': 'system', 'content': 'Summarize the key topics and emotions.'},
                  {'role': 'user', 'content': content}]
    )
    return resp.choices[0].message.content

# Highlight sweet messages
def highlight_sweet(memory):
    msgs = memory.get_all()
    content = '\n'.join(m.content for m in msgs)
    resp = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[{'role': 'system', 'content': 'Identify the most affectionate and emotional messages.'},
                  {'role': 'user', 'content': content}]
    )
    return resp.choices[0].message.content

