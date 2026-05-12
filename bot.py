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
            password="https://dsc.gg/ajidevserver",
            secure=False
        ),
        wavelink.Node(
            uri="https://lavalink.devamop.in:443",
            password="DevamOP",
            secure=True
        )
    ]
    
    await wavelink.Pool.connect(nodes=nodes, client=bot)
    print("✅ Attempted to connect to Lavalink nodes...")

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"✅ Lavalink Node Connected Successfully: {node.uri}")

@bot.event
async def on_wavelink_node_closed(node: wavelink.Node, payload):
    print(f"❌ Lavalink Node Disconnected: {node.uri} | Reason: {payload.reason}")

# ====================== PLAY COMMAND ======================
@bot.command()
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Join a voice channel first!")

    # Connect to voice
    if not ctx.voice_client:
        try:
            await ctx.author.voice.channel.connect(cls=wavelink.Player)
            await ctx.send("🔗 Joined voice channel!")
        except Exception as e:
            return await ctx.send(f"❌ Failed to join voice: {e}")

    player: wavelink.Player = ctx.voice_client

    await ctx.send(f"🔍 Searching: **{query}**")
    
    tracks = await wavelink.Playable.search(query)
    if not tracks:
        return await ctx.send("❌ No tracks found!")

    track = tracks[0]
    await player.play(track)
    await ctx.send(f"▶️ **Now Playing:** {track.title}")

bot.run(TOKEN)