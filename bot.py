import discord
import os
import io
import traceback
import sys
import time
import datetime
import asyncio
import random
import aiohttp
import pip
import random
import textwrap
from contextlib import redirect_stdout
from discord.ext import commands
import json
bot = commands.Bot(command_prefix=commands.when_mentioned_or('*'),description="The revamped dat banana bot made by dat banana boi#1982.\n\nHelp Commands",owner_id=277981712989028353)
bot.remove_command("help")
bot.load_extension("cogs.math")
bot.load_extension("cogs.mod")
bot.load_extension("cogs.utility")
bot.load_extension("cogs.fun")
bot.load_extension("cogs.info")
bot.load_extension("cogs.developer")
bot.load_extension("cogs.cr")
bot.load_extension("cogs.help")
bot.load_extension("cogs.coc")
#bot.load_extension("cogs.lol")



def cleanup_code(content):
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    return content.strip('` \n')
    
  
@bot.event
async def on_ready():
    print('Bot is online, and ready to ROLL!')
    while True:
        await bot.change_presence(game=discord.Game(name=f"with {len(bot.guilds)} servers!"))
        await asyncio.sleep(15)
        await bot.change_presence(game=discord.Game(name="using *help!"))
        await asyncio.sleep(15)
        await bot.change_presence(game=discord.Game(name="in v6.0, BETA."))
        await asyncio.sleep(15)

@bot.event
async def on_guild_join(guild):
    lol = bot.get_channel(392443319684300801)
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "dat banana bot has arrived in a new server!"
    em.description = f"Server: {guild}"
    await lol.send(embed=em)
    await ctx.send(f"Hiya, guys in **{guild.name}**! Thanks for welcoming me! I am dat banana bot, a gud Discord bot. Try me out by typing *help!")


@bot.event
async def on_guild_remove(guild):
    lol = bot.get_channel(392443319684300801)
    em = discord.Embed(color=discord.Color(value=0xf44242))
    em.title = "dat banana bot has been removed from a server."
    em.description = f"Server: {guild}"
    await lol.send(embed=em)

    
@bot.event
async def when_mentioned():
    await ctx.send("BAH! Couldn't find enough people to ping, could you? Anyway, I'm dat banana bot, made by dat banana boi#1982. Type *help to see what I can do for you today.")   
            
        
def dev_check(id):
    with open('data/devs.json') as f:
        devs = json.load(f)
    if id in devs:
        return True
    return False
            
            
@bot.command(name='presence')
@commands.is_owner()
async def _set(ctx, Type=None,*,thing=None):
    """What AM I doing?!?!?!"""
    if Type is None:
        await ctx.send('Do it right, plz! Usage: *presence [game/stream] [msg]')
    else:
      if Type.lower() == 'stream':
        await bot.change_presence(game=discord.game(name=thing,type=1,url='https://www.twitch.tv/a'),status='online')
        await ctx.send(f'Aye aye, I am now streaming {thing}!')
      elif Type.lower() == 'game':
        await bot.change_presence(game=discord.game(name=thing))
        await ctx.send(f'Aye aye, I am now playing {thing}!')
      elif Type.lower() == 'clear':
        await bot.change_presence(game=None)
        await ctx.send('Aye aye, I am not playing anything, anymore!')
      else:
        await ctx.send('Want me to do something? YOU do it right first. Usage: *presence [game/stream] [msg]')

                
@bot.command()
async def bug(ctx, *, msg:str):
    """Got a PROB? Tell us about it...  """
    lol = bot.get_channel(373917178547929088)
    color = discord.Color(value=0x00ff00)
    em=discord.Embed(color=color, title="Bug reported!")
    em.description = f"Bug: {msg}"
    em.set_footer(text=f"Bug sent by {ctx.message.author.name}")                         
    await ctx.send("Thanks for reporting that bug! :bug: We will get back to you ASAP.")                     
 
                
@bot.command()
async def say(ctx, *, message:str):
    '''I say what you want me to say. Oh boi...'''
    await ctx.message.delete()
    await ctx.send(message)                   
                       

@bot.command()
async def ping(ctx):
    """Premium ping pong giving you a websocket latency."""
    color = discord.Color(value=0x00ff00)
    em = discord.Embed(color=color, title='PoIIIng! Your supersonic latency is:')
    em.description = f"{bot.latency * 1000:.4f} ms"
    em.set_footer(text="Psst...A heartbeat is 27 ms!")
    await ctx.send(embed=em)
  
        
@bot.command()
async def invite(ctx):
    """Allow my bot to join the hood. YOUR hood."""
    await ctx.send("Lemme join that hood -> https://discordapp.com/oauth2/authorize?client_id=388476336777461770&scope=bot&permissions=2146958591")                       

                       
@bot.command(name='discord')
async def _discord(ctx):
    """We have an awesome hood to join, join now!"""
    await ctx.send("Your turn to join the hood -> https://discord.gg/wvkVknA")

                      
@bot.command(hidden=True, name='eval')
async def _eval(ctx, *, body: str):

    if not dev_check(ctx.author.id):
        return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")

    env = {
        'bot': bot,
        'ctx': ctx,
        'channel': ctx.channel,
        'author': ctx.author,
        'guild': ctx.guild,
        'message': ctx.message,
    }

    env.update(globals())

    body = cleanup_code(body)
    stdout = io.StringIO()

    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    try:
        exec(to_compile, env)
    except Exception as e:
        return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

    func = env['func']
    try:
        with redirect_stdout(stdout):
            ret = await func()
    except Exception as e:
        value = stdout.getvalue()
        await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
    else:
        value = stdout.getvalue()
        try:
            await ctx.message.add_reaction('\u2705')
        except:
            pass

        if ret is None:
            if value:
                await ctx.send(f'```py\n{value}\n```')
        else:
            await ctx.send(f'```py\n{value}{ret}\n```')    
                       
                       

bot.run("Mzg4NDc2MzM2Nzc3NDYxNzcw.DVEeCw.eAXnUyjQHwRQFUEubFoF1fRxrQ0")
