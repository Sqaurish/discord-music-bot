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
    print(f"✅ Lavalink Node Ready!")

# Get player helper function
def get_player(ctx):
    return ctx.voice_client if isinstance(ctx.voice_client, wavelink.Player) else None

# ====================== COMMANDS ======================

@bot.command()
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Join a voice channel first!")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect(cls=wavelink.Player)

    player: wavelink.Player = ctx.voice_client
    await ctx.send(f"🔍 Searching: **{query}**")

    tracks = await wavelink.Playable.search(query)
    if not tracks:
        return await ctx.send("❌ No tracks found!")

    track = tracks[0]
    await player.play(track)
    await ctx.send(f"▶️ **Now Playing:** {track.title} by {track.author}")


@bot.command()
async def pause(ctx):
    player = get_player(ctx)
    if not player or not player.playing:
        return await ctx.send("❌ Nothing is playing right now!")

    await player.pause()
    await ctx.send("⏸️ **Paused**")


@bot.command()
async def resume(ctx):
    player = get_player(ctx)
    if not player or not player.paused:
        return await ctx.send("❌ Nothing is paused!")

    await player.resume()
    await ctx.send("▶️ **Resumed**")


@bot.command()
async def skip(ctx):
    player = get_player(ctx)
    if not player or not player.playing:
        return await ctx.send("❌ Nothing is playing!")

    await player.skip()
    await ctx.send("⏭️ **Skipped**")


@bot.command()
async def stop(ctx):
    player = get_player(ctx)
    if player:
        await player.disconnect()
        await ctx.send("⏹️ Stopped and disconnected.")
    else:
        await ctx.send("❌ Bot is not in voice channel.")


@bot.command()
async def queue(ctx):
    player = get_player(ctx)
    if not player:
        return await ctx.send("❌ Bot is not in a voice channel.")

    if not player.playing and not player.queue:
        return await ctx.send("Queue is empty.")

    embed = discord.Embed(title="🎵 Music Queue", color=0x00b0ff)
    
    if player.playing and player.current:
        embed.add_field(name="Now Playing", value=f"**{player.current.title}**", inline=False)
    
    if player.queue:
        q = "\n".join([f"`{i+1}.` {track.title}" for i, track in enumerate(player.queue)])
        embed.add_field(name="Up Next", value=q[:900], inline=False)

    await ctx.send(embed=embed)

bot.run(TOKEN)