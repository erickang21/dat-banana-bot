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
import random
import textwrap
import inspect
from contextlib import redirect_stdout
from discord.ext import commands
import json


def getprefix(bot, message):
    with open("data/prefix.json") as f:
        x = json.loads(f.read())
    pre = x.get(str(message.guild.id), "*")
    return pre 


bot = commands.Bot(command_prefix=getprefix,description="The revamped dat banana bot made by dat banana boi#1982.\n\nHelp Commands",owner_id=277981712989028353)
bot._last_result = None
session = aiohttp.ClientSession()
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
bot.load_extension("cogs.lol")
bot.load_extension("cogs.economy")
bot.load_extension("cogs.dbl")
bot.load_extension("cogs.music")
bot.load_extension("cogs.idiotic")

def cleanup_code(content):
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    return content.strip('` \n')
    

def dev_check(id):
    with open('data/devs.json') as f:
        devs = json.load(f)
        if id in devs:
            return True
        return False  


def modlog_check(guildid):
    with open('data/modlog.json') as f:
        x = json.loads(f.read())
    try:
        x[str(guildid)]
        return True
    except KeyError:
        return False


@bot.event
async def on_ready():
    print('Bot is online, and ready to ROLL!')
    while True:
        await bot.change_presence(activity=discord.Game(name=f"with {len(bot.guilds)} servers!"))
        await asyncio.sleep(15)
        await bot.change_presence(activity=discord.Game(name="using *help!"))
        await asyncio.sleep(15)
        await bot.change_presence(activity=discord.Game(name="v6.0.6"))
        await asyncio.sleep(15)


@bot.event
async def on_message_edit(before, after):
    if modlog_check(before.guild.id):
        with open("data/modlog.json") as f:
            x = json.loads(f.read())
        try:
            lol = bot.get_channel(x[str(before.guild.id)])
            em = discord.Embed(color=discord.Color(value=0x00ff00), title='Message Edited')
            em.add_field(name='Channel', value=f"<#{before.channel.id}>")
            em.add_field(name='Content Before', value=before.content)
            em.add_field(name='Content After', value=after.content)
            em.add_field(name='Sent By', value=str(before.author))
            await lol.send(embed=em)
        except KeyError:
            pass
    else:
        pass



@bot.event
async def on_guild_join(guild):
    lol = bot.get_channel(392443319684300801)
    em = discord.Embed(color=discord.Color(value=0x00ff00))
    em.title = "dat banana bot has joined a new server!"
    em.description = f"**{guild.name}**"
    em.set_footer(text=f"ID: {guild.id}")
    em.set_thumbnail(url=guild.icon_url)
    await lol.send(embed=em)
    await guild.channels[0].send(f"Hiya, guys in **{guild.name}**! Thanks for welcoming me! I am dat banana bot, a gud Discord bot. Try me out by typing *help!")


@bot.event
async def on_guild_remove(guild):
    lol = bot.get_channel(392443319684300801)
    em = discord.Embed(color=discord.Color(value=0xf44242))
    em.title = "dat banana bot has been removed from a server."
    em.description = f"**{guild.name}**"
    em.set_footer(text=f"ID: {guild.id}")
    em.set_thumbnail(url=guild.icon_url)
    await lol.send(embed=em)

    
@bot.event
async def on_member_join(member):
    with open("data/welcomemsg.json") as f:
        x = json.loads(f.read())
    try:
        channel = x[str(member.guild.id)]
    except KeyError:
        return
    if channel is False:
        pass
    else:
        lol = bot.get_channel(channel)
        await lol.send(f"Hello {member.mention}! Welcome to **{member.guild.name}**, have a great time!")
    if modlog_check(member.guild.id):
        with open("data/modlog.json") as f:
            x = json.loads(f.read())
        lol = bot.get_channel(x[str(member.guild.id)])
        em = discord.Embed(color=discord.Color(value=0x00ff00), title='Member Joined')
        em.add_field(name="Name", value=str(member))
        em.add_field(name='Joined At', value=str(member.joined_at.strftime("%b %m, %Y, %A, %I:%M %p")))
        em.add_field(name="ID", value=member.id)
        em.set_thumbnail(url=member.avatar_url)
        await lol.send(embed=em)
    else:
        pass


@bot.event
async def on_member_remove(member):
    if modlog_check(member.guild.id):
        with open("data/modlog.json") as f:
            x = json.loads(f.read())
        lol = bot.get_channel(x[str(member.guild.id)])
        em = discord.Embed(color=discord.Color(value=0x00ff00), title='Member Left')
        em.add_field(name="Name", value=str(member))
        em.add_field(name="ID", value=member.id)
        em.set_thumbnail(url=member.avatar_url)
        await lol.send(embed=em)
    else:
        pass


@bot.event
async def on_message_delete(message):
    if modlog_check(message.guild.id):
        with open("data/modlog.json") as f:
            x = json.loads(f.read())
        try:
            lol = bot.get_channel(x[str(message.guild.id)])
            em = discord.Embed(color=discord.Color(value=0x00ff00), title='Message Deleted')
            em.add_field(name='Content', value=message.content)
            em.add_field(name='Sent By', value=str(message.author))
            em.add_field(name='Channel', value=f"<#{message.channel.id}>")
            await lol.send(embed=em)
        except KeyError:
            pass
    else:
        pass




@bot.event
async def on_command_error(ctx, error):
    em = discord.Embed(color=discord.Color(value=0xf44e42), title='An error occurred.')
    if isinstance(error, commands.NotOwner):
        em.description = 'Not my daddy! This command is for the owner only.'
        return await ctx.send(embed=em)
    elif isinstance(error, commands.MissingPermissions):
        em.description = 'You are missing permissions required to run this command.'
        return await ctx.send(embed=em)
    elif isinstance(error, commands.CommandOnCooldown):
        em.description = f'The command is on cooldown! You can use it again in:\n{error.retry_after/60:.0f} minutes.'
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(error)

            
            
@bot.command(name='presence')
@commands.is_owner()
async def _set(ctx, Type=None,*,thing=None):
    """What AM I doing?!?!?!"""
    if Type is None:
        await ctx.send('Do it right, plz! Usage: *presence [game/stream] [msg]')
    else:
      if Type.lower() == 'stream':
        await bot.change_presence(activity=discord.Game(name=thing,type=1,url='https://www.twitch.tv/a'),status='online')
        await ctx.send(f'Aye aye, I am now streaming {thing}!')
      elif Type.lower() == 'game':
        await bot.change_presence(activity=discord.Game(name=thing))
        await ctx.send(f'Aye aye, I am now playing {thing}!')
      elif Type.lower() == 'clear':
        await bot.change_presence(activity=None)
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
async def say(ctx, *, message: commands.clean_content()):
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

                      
@bot.command(name='eval')
async def _eval(ctx, *, body):
    """Evaluates python code"""
    if not dev_check(ctx.author.id):
        return await ctx.send("You cannot use this because you are not a developer.")
    env = {
        'ctx': ctx,
        'channel': ctx.channel,
        'author': ctx.author,
        'guild': ctx.guild,
        'message': ctx.message,
        '_': bot._last_result,
    }

    env.update(globals())

    body = cleanup_code(body)
    stdout = io.StringIO()
    err = out = None

    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    def paginate(text: str):
        '''Simple generator that paginates text.'''
        last = 0
        pages = []
        for curr in range(0, len(text)):
            if curr % 1980 == 0:
                pages.append(text[last:curr])
                last = curr
                appd_index = curr
        if appd_index != len(text) - 1:
            pages.append(text[last:curr])
        return list(filter(lambda a: a != '', pages))

    try:
        exec(to_compile, env)
    except Exception as e:
        err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
        return await ctx.message.add_reaction('\u2049')

    func = env['func']
    try:
        with redirect_stdout(stdout):
            ret = await func()
    except Exception as e:
        value = stdout.getvalue()
        err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
    else:
        value = stdout.getvalue()
        if ret is None:
            if value:
                try:

                    out = await ctx.send(f'```py\n{value}\n```')
                except:
                    paginated_text = paginate(value)
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f'```py\n{page}\n```')
                            break
                        await ctx.send(f'```py\n{page}\n```')
        else:
            bot._last_result = ret
            try:
                out = await ctx.send(f'```py\n{value}{ret}\n```')
            except:
                paginated_text = paginate(f"{value}{ret}")
                for page in paginated_text:
                    if page == paginated_text[-1]:
                        out = await ctx.send(f'```py\n{page}\n```')
                        break
                    await ctx.send(f'```py\n{page}\n```')

    if out:
        await ctx.message.add_reaction('\u2705')  # tick
    elif err:
        await ctx.message.add_reaction('\u2049')  # x
    else:
        await ctx.message.add_reaction('\u2705')
                       
                       
#if __name__ != "__main__": 
#    print("Bot did not start with the main file (bot.py).")
#if bot.user.id != 388476336777461770:
#    print("The bot files are not being hosted on the bot user: dat banana bot#0170. Please do not host other instances of the bot.")
with open("data/apikeys.json") as f:
    x = json.loads(f.read())
try:
    bot.run(x['bottoken'])
except Exception as e:
    print("Could not start the bot. Check the token.")
