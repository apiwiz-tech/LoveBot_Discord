import os
import discord
from discord.ext import commands, tasks
from memory import MemoryStore
from openai import OpenAI

# Initialize OpenAI client with your environment variable key
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='@LoveBot ', intents=intents)
memory = MemoryStore()

# --- OpenAI-powered helper functions ---
def analyze_message(text):
    response = client.chat.completions.create(
        model='gpt-4',
        messages=[
            {'role': 'system', 'content': 'Analyze emotional tone and personality traits.'},
            {'role': 'user', 'content': text}
        ]
    )
    return response.choices[0].message.content

def detect_argument_with_gpt(messages):
    conversation = '\n'.join(messages)
    prompt = (
        "You are a relationship AI. Given this conversation, "
        "determine if there is an argument or tension. Reply with YES or NO."
        f"\nConversation:\n{conversation}"
    )
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}]
    )
    answer = response.choices[0].message.content.strip().upper()
    return answer == 'YES'

def generate_intervention_with_gpt(messages):
    conversation = '\n'.join(messages)
    prompt = (
        "You are a compassionate AI relationship counselor. "
        "The following conversation has some tension. "
        "Provide a gentle, constructive message to help both people calm down and reflect."
        f"\nConversation:\n{conversation}"
    )
    response = client.chat.completions.create(
        model='gpt-4',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.choices[0].message.content.strip()

def explain_conflict_with_gpt(messages):
    conversation = '\n'.join(messages)
    prompt = (
        "You are an expert relationship counselor AI. "
        "Analyze the following conversation and explain what the conflict is about. "
        "Give constructive advice on how to resolve it."
        f"\nConversation:\n{conversation}"
    )
    response = client.chat.completions.create(
        model='gpt-4',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.choices[0].message.content.strip()

def summarize_week(memory):
    msgs = memory.get_recent(days=7)
    content = '\n'.join(m.content for m in msgs)
    response = client.chat.completions.create(
        model='gpt-4',
        messages=[
            {'role': 'system', 'content': 'Summarize the key topics and emotions.'},
            {'role': 'user', 'content': content}
        ]
    )
    return response.choices[0].message.content

def highlight_sweet(memory):
    msgs = memory.get_all()
    content = '\n'.join(m.content for m in msgs)
    response = client.chat.completions.create(
        model='gpt-4',
        messages=[
            {'role': 'system', 'content': 'Identify the most affectionate and emotional messages.'},
            {'role': 'user', 'content': content}
        ]
    )
    return response.choices[0].message.content


# --- Discord Bot Events & Commands ---

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    weekly_summary.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Log and analyze
    memory.log_message(message)
    analysis = analyze_message(message.content)
    memory.store_analysis(message, analysis)

    recent_msgs = memory.get_last_messages_content(limit=10)

    # Detect argument & intervene
    if detect_argument_with_gpt(recent_msgs):
        intervention = generate_intervention_with_gpt(recent_msgs)
        await message.channel.send(intervention)

    await bot.process_commands(message)

@bot.command(name='summary')
async def summary(ctx):
    summary_text = summarize_week(memory)
    await ctx.send(f"Weekly Summary:\n{summary_text}")

@bot.command(name='highlights')
async def highlights(ctx):
    highlights_text = highlight_sweet(memory)
    await ctx.send(f"Sweet Moments:\n{highlights_text}")

@bot.command(name='why-fight')
async def why_fight(ctx):
    recent_msgs = memory.get_last_messages_content(limit=10)
    explanation = explain_conflict_with_gpt(recent_msgs)
    await ctx.send(f"Conflict Analysis:\n{explanation}")

@tasks.loop(hours=168)  # 168 hours = 7 days
async def weekly_summary():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print(f"Guild with ID {GUILD_ID} not found.")
        return
    channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
    if channel is None:
        print("No suitable channel found to send weekly summary.")
        return
    summary_text = summarize_week(memory)
    await channel.send(f"📅 **Weekly Relationship Recap**\n{summary_text}")

if __name__ == '__main__':
    bot.run(TOKEN)
