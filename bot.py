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
    
    nodes = [
        wavelink.Node(
            uri="https://lavalink.devamop.in:443",
            password="DevamOP",
            secure=True
        )
    ]
    
    await wavelink.Pool.connect(nodes=nodes, client=bot)
    print("✅ Connected to Lavalink!")

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"✅ Lavalink Node is Ready!")

# ====================== COMMANDS ======================

@bot.command()
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        return await ctx.send("❌ You must be in a voice channel first!")

    # === Improved Voice Connection ===
    player: wavelink.Player = ctx.voice_client

    if not player:
        try:
            player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            await ctx.send("🔗 Joined voice channel!")
        except Exception as e:
            return await ctx.send(f"❌ Failed to join voice: {e}")

    # Make sure bot and user are in same channel
    if player.channel != ctx.author.voice.channel:
        await player.move_to(ctx.author.voice.channel)

    await ctx.send(f"🔍 Searching for: **{query}**")

    tracks = await wavelink.Playable.search(query)
    if not tracks:
        return await ctx.send("❌ No results found!")

    track = tracks[0]
    await player.play(track)
    await ctx.send(f"▶️ **Now Playing:** {track.title}\nBy: {track.author}")


@bot.command()
async def pause(ctx):
    player: wavelink.Player = ctx.voice_client
    if not player or not player.playing:
        return await ctx.send("❌ Nothing is playing!")
    await player.pause()
    await ctx.send("⏸️ Paused")


@bot.command()
async def resume(ctx):
    player: wavelink.Player = ctx.voice_client
    if not player or not player.paused:
        return await ctx.send("❌ Nothing is paused!")
    await player.resume()
    await ctx.send("▶️ Resumed")


@bot.command()
async def skip(ctx):
    player: wavelink.Player = ctx.voice_client
    if not player or not player.playing:
        return await ctx.send("❌ Nothing is playing!")
    await player.skip()
    await ctx.send("⏭️ Skipped")


@bot.command()
async def stop(ctx):
    player: wavelink.Player = ctx.voice_client
    if player:
        await player.disconnect()
        await ctx.send("⏹️ Stopped and left the voice channel.")
    else:
        await ctx.send("❌ Bot is not in a voice channel.")


bot.run(TOKEN)