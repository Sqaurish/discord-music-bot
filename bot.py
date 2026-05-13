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

# Helper function to get player
def get_player(ctx):
    vc = ctx.voice_client
    return vc if isinstance(vc, wavelink.Player) else None

# ====================== COMMANDS ======================

@bot.command()
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Join a voice channel first!")

    # Join VC if not joined
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect(cls=wavelink.Player)

    player: wavelink.Player = get_player(ctx)

    await ctx.send(f"🔍 Searching: **{query}**")
    tracks = await wavelink.Playable.search(query)

    if not tracks:
        return await ctx.send("❌ No tracks found!")

    track = tracks[0]
    await player.queue.put_wait(track)

    if not player.playing:
        await player.play(track)
        await ctx.send(f"▶️ **Now Playing:** {track.title}")
    else:
        await ctx.send(f"✅ **Added to queue:** {track.title}")


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
async def queue(ctx):
    player = get_player(ctx)
    if not player:
        return await ctx.send("❌ Bot is not in a voice channel.")

    embed = discord.Embed(title="🎵 Music Queue", color=0x3498db)

    if player.current:
        embed.add_field(name="Now Playing", value=f"▶️ {player.current.title}", inline=False)

    if player.queue:
        q_list = "\n".join([f"`{i+1}.` {track.title}" for i, track in enumerate(player.queue)])
        embed.add_field(name="Up Next", value=q_list[:900] or "Empty", inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def stop(ctx):
    player = get_player(ctx)
    if player:
        await player.disconnect()
        await ctx.send("⏹️ Stopped and left voice channel.")
    else:
        await ctx.send("❌ Bot is not in voice.")

bot.run(TOKEN)