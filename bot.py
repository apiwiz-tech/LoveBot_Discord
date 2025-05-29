### `bot.py`
python
import os
import discord
from discord.ext import commands, tasks
from analyzer import analyze_message, detect_argument, summarize_week, highlight_sweet
from memory import MemoryStore

# Load environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')
GUILD_ID = int(os.getenv('GUILD_ID'))  # your private server ID

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='@LoveBot ', intents=intents)
memory = MemoryStore()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    weekly_summary.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # Log message
    memory.log_message(message)
    # Analyze
    analysis = analyze_message(message.content)
    memory.store_analysis(message, analysis)
    # Check for argument
    if detect_argument(message.content):
        reply = memory.generate_intervention(message)
        await message.channel.send(reply)
    await bot.process_commands(message)

# Commands
@bot.command(name='summary')
async def summary(ctx):
    summary_text = summarize_week(memory)
    await ctx.send(f"Weekly Summary:\n{summary_text}")

@bot.command(name='highlights')
async def highlights(ctx):
    highlights = highlight_sweet(memory)
    await ctx.send(f"Sweet Moments:\n{highlights}")

@bot.command(name='why-fight')
async def why_fight(ctx):
    explanation = memory.explain_conflict()
    await ctx.send(f"Conflict Analysis:\n{explanation}")

# Scheduled task
tasks.Loop = tasks.loop
def weekly_summary():
    channel = bot.get_guild(GUILD_ID).text_channels[0]
    summary_text = summarize_week(memory)
    channel.send(f"📅 **Weekly Relationship Recap**\n{summary_text}")

if __name__ == '__main__':
    bot.run(TOKEN)
