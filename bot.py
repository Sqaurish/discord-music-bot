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
            uri="http://lava-v4.ajieblogs.eu.org:80",
            password="https://dsc.gg/ajidevserver"
        )
    ]
    
    await wavelink.Pool.connect(nodes=nodes, client=bot)
    print("🔄 Connecting to Lavalink...")

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"✅ Lavalink Connected → {node.uri}")

def get_player(ctx):
    vc = ctx.voice_client
    return vc if isinstance(vc, wavelink.Player) else None

# ====================== COMMANDS ======================

@bot.command()
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Join a voice channel first!")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect(cls=wavelink.Player)

    player: wavelink.Player = get_player(ctx)

    await ctx.send(f"🔍 Searching: **{query}**")
    tracks = await wavelink.Playable.search(query)

    if not tracks:
        return await ctx.send("❌ No tracks found!")

    track = tracks[0]
    await player.queue.put_wait(track)

    if not player.playing and not player.paused:
        await player.play(track)
        await ctx.send(f"▶️ **Now Playing:** {track.title}")
    else:
        await ctx.send(f"✅ **Added to queue:** {track.title}")


@bot.command()
async def insert(ctx, *, query: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Join a voice channel first!")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect(cls=wavelink.Player)

    player: wavelink.Player = get_player(ctx)
    tracks = await wavelink.Playable.search(query)

    if not tracks:
        return await ctx.send("❌ No tracks found!")

    track = tracks[0]
    player.queue.put_at_front(track)

    if not player.playing and not player.paused:
        await player.play(track)
        await ctx.send(f"▶️ **Now Playing:** {track.title}")
    else:
        await ctx.send(f"⏭️ **Inserted to play next:** {track.title}")


@bot.command()
async def pause(ctx):
    player = get_player(ctx)
    if not player or not player.playing:
        return await ctx.send("❌ Nothing is playing!")
    await player.pause()
    await ctx.send("⏸️ **Paused**")


@bot.command()
async def resume(ctx):
    player = get_player(ctx)
    if not player or not player.paused:
        return await ctx.send("❌ Nothing is paused!")
    await player.resume()
    await ctx.send("▶️ **Resumed**")


@bot.command(aliases=['np'])
async def nowplaying(ctx):
    player = get_player(ctx)
    if not player or not player.current:
        return await ctx.send("❌ Nothing is playing!")
    track = player.current
    await ctx.send(f"🎵 **Now Playing:** {track.title}\nBy: {track.author}")


@bot.command()
async def skip(ctx):
    player = get_player(ctx)
    if not player or not player.playing:
        return await ctx.send("❌ Nothing is playing!")
    await player.skip()
    await ctx.send("⏭️ **Skipped**")


@bot.command()
async def loop(ctx):
    player = get_player(ctx)
    if not player:
        return await ctx.send("❌ Not in voice!")
    player.queue.loop = not player.queue.loop
    status = "Enabled" if player.queue.loop else "Disabled"
    await ctx.send(f"🔁 Loop **{status}**")


@bot.command()
async def volume(ctx, volume: int = 100):
    player = get_player(ctx)
    if not player:
        return await ctx.send("❌ Not in voice!")
    volume = max(0, min(150, volume))
    await player.set_volume(volume)
    await ctx.send(f"🔊 Volume set to **{volume}%**")


@bot.command()
async def queue(ctx):
    player = get_player(ctx)
    if not player:
        return await ctx.send("❌ Bot is not in voice.")

    embed = discord.Embed(title="🎵 Music Queue", color=0x00b0ff)
    if player.current:
        embed.add_field(name="Now Playing", value=f"▶️ {player.current.title}", inline=False)
    if player.queue:
        q = "\n".join([f"`{i+1}.` {track.title}" for i, track in enumerate(player.queue)])
        embed.add_field(name="Up Next", value=q[:900], inline