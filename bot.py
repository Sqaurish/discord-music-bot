import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

queues = {}

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = []
    return queues[guild_id]

@bot.command(name='play')
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ You need to join a voice channel first!")
    
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
    
    await ctx.send(f"🔍 Searching: **{search}**")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)
        if 'entries' in info:
            info = info['entries'][0]
    
    song = {'url': info['url'], 'title': info.get('title', 'Unknown Song')}
    
    queue = get_queue(ctx.guild.id)
    queue.append(song)
    
    await ctx.send(f"✅ Added to queue: **{song['title']}**")
    
    if not ctx.voice_client.is_playing():
        await play_next(ctx)

async def play_next(ctx):
    queue = get_queue(ctx.guild.id)
    if not queue:
        return await ctx.send("🎵 Queue finished.")
    
    song = queue.pop(0)
    
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    
    def after(error):
        if error:
            print(error)
        asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
    
    source = discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS)
    ctx.voice_client.play(source, after=after)
    
    await ctx.send(f"▶️ Now playing: **{song['title']}**")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped!")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        queues[ctx.guild.id] = []
        await ctx.send("⏹️ Stopped and disconnected.")

bot.run(TOKEN)