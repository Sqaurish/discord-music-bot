import discord
from discord.ext import commands
import wavelink
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')
    
    # Connect to Lavalink
    nodes = [wavelink.Node(
        uri="http://lava-v4.ajieblogs.eu.org:80",   # Change if needed
        password="https://dsc.gg/ajidevserver"
    )]
    
    await wavelink.Pool.connect(nodes=nodes, client=bot)
    print("✅ Connected to Lavalink!")

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Join a voice channel first!")
    
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect(cls=wavelink.Player)
    
    tracks = await wavelink.Playable.search(search)
    if not tracks:
        return await ctx.send("❌ No results found!")
    
    track = tracks[0]
    player: wavelink.Player = ctx.voice_client
    
    await player.play(track)
    await ctx.send(f"▶️ Now playing: **{track.title}**")

@bot.command()
async def skip(ctx):
    player: wavelink.Player = ctx.voice_client
    if player and player.playing:
        await player.skip()
        await ctx.send("⏭️ Skipped!")

@bot.command()
async def stop(ctx):
    player: wavelink.Player = ctx.voice_client
    if player:
        await player.disconnect()
        await ctx.send("⏹️ Stopped!")

bot.run(TOKEN)