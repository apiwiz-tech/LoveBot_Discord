import os
import discord
from discord.ext import commands, tasks
from aiohttp import web
import asyncio

from analyzer import (
    analyze_message,
    detect_argument_with_gpt,
    generate_intervention_with_gpt,
    summarize_week,
    highlight_sweet,
    explain_conflict_with_gpt
)
from memory import MemoryStore

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True


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

    # Log and analyze
    memory.log_message(message)
    analysis = await analyze_message(message.content)
    memory.store_analysis(message, analysis)

    recent_msgs = memory.get_last_messages_content(limit=10)

    # Detect argument & intervene
    if await detect_argument_with_gpt(recent_msgs):
        intervention = await generate_intervention_with_gpt(recent_msgs)
        await message.channel.send(intervention)

    await bot.process_commands(message)

@bot.command(name='summary')
async def summary(ctx):
    summary_text = await summarize_week(memory)
    await ctx.send(f"Weekly Summary:\n{summary_text}")

@bot.command(name='highlights')
async def highlights(ctx):
    highlights_text = await highlight_sweet(memory)
    await ctx.send(f"Sweet Moments:\n{highlights_text}")

@bot.command(name='why-fight')
async def why_fight(ctx):
    recent_msgs = memory.get_last_messages_content(limit=10)
    explanation = await explain_conflict_with_gpt(recent_msgs)
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
    summary_text = await summarize_week(memory)
    await channel.send(f"📅 **Weekly Relationship Recap**\n{summary_text}")

# --- HTTP server for Render health check ---

PORT = int(os.environ.get("PORT", 8000))

async def handle(request):
    return web.Response(text="Bot is running")

async def start_http_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# --- Main async entry point to run bot and HTTP server concurrently ---

async def main():
    await start_http_server()
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
