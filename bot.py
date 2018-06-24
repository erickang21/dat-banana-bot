import discord
import re
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
import ezjson
import colorama
from motor.motor_asyncio import AsyncIOMotorClient
from ext.context import DatContext
from ext.logger import Logger as logger

colorama.init()

with open("data/apikeys.json") as f:
    x = json.load(f)
db = AsyncIOMotorClient(x['mongodb'])


async def getprefix(bot, message):
    if isinstance(message.channel, discord.DMChannel): return "*"
    x = await db.datbananabot.prefix.find_one({"id": str(message.guild.id)})
    pre = x['prefix'] if x is not None else '*'
    match = re.match(f"<@!?{bot.user.id}> ", message.content)
    return match.group() if match else pre


bot = commands.Bot(command_prefix=getprefix,description="The revamped dat banana bot made by dat banana boi#1982.\n\nHelp Commands",owner_id=277981712989028353)
bot._last_result = None
bot.session = aiohttp.ClientSession()
bot.starttime = time.time()
bot.commands_run = 0
bot.logger = logger
with open("data/apikeys.json") as f:
    x = json.load(f)
bot.db = db.datbananabot
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
bot.load_extension("cogs.nsfw")



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


# async def process_commands(message):
#     ctx = await bot.get_context(message, cls=DatContext)
#     if not ctx.command:
#         return
#     await bot.invoke(ctx)

async def modlog_check(guildid):
    x = await bot.db.modlog.find_one({'id': str(guildid)})
    if not x:
        return False
    return True


async def get_modlog_channel(guildid):
    x = await bot.db.modlog.find_one({'id': str(guildid)})
    return int(x['channel'])

@bot.event
async def on_ready():
    if bot.user.id != 388476336777461770:
        print("COPYING ALERT! COULD NOT IDENTIFY BOT USER! EXPOSED!")
        exit() # :p
    bot.session = aiohttp.ClientSession()
    presence = [
        "*help | BOIIIIIII!",
        "*help | 🍌 are like my life: always by my side.",
        "*help | Live and die by the 🍌.",
        "*help | Who took my 🍌?",
        "*help | Fortnite succ CcCcC.",
        "*help | ur mum a trap",
        "*help | ur universe trans",
        "*help | LoL > Fortnite",
        "*help | 🍌. The stuff of life.",
        "*help | Hmm. Hmm?",
        "*help | Looking for smexy weebs? See my JS sister...",
        "*help | https://discord.gg/3Nxb7yZ (where I belong)",
        "*help | REEEEEEEEEE",
        "*help | gib 🍌 plox",
        f"*help | in {len(bot.guilds)} servers!",
        "*help | skrrrrrrrrra pa pa pa pa pa.",
        "*help | asdfasdfasdfasdf.",
        "*help | Git Gud At Leagye.",
        "*help | Music officially fixed! YEET"
    ]
    print('Bot is online, and ready to ROLL!')
    while True:
        await bot.change_presence(activity=discord.Game(name=random.choice(presence)))
        await asyncio.sleep(10)


@bot.event
async def on_message(message):
    if re.match(f"^<@!?{bot.user.id}>$", message.content):
        await message.channel.send(f"{bot.get_emoji(430853515217469451)} BAH! Why you :regional_indicator_p:ing me? Anyway, I'm dat banana bot, so nice to meet you. I do a LOT of kewl stuff, like music, starboard, welcome/leave messages, Canvas, and so much more! All it takes is `*help` to see the powers I got! {bot.get_emoji(430853629570711562)}")
    if re.findall(r"(http(s)://|)(discord.gg|discord.io|discordapp.com/invite)\S+", message.content):
        x = await bot.db.antilink.find_one({"id": message.guild.id})
        if not x:
            return
        if not x['status']:
            return
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        await message.channel.send(f"Hey, {message.author.mention}! No advertising allowed in this server. Get that invite link out of here!")
        if await modlog_check(message.guild.id):
            try:
                lol = bot.get_channel(await get_modlog_channel(message.guild.id))
                em = discord.Embed(color=0x00ff00, title='An invite was posted.')
                em.add_field(name='Channel', value=f"<#{message.channel.id}>")
                em.add_field(name='Link', value=message.content)
                em.add_field(name='Sent By', value=str(message.author))
                await lol.send(embed=em)
            except KeyError:
                pass

    if not message.author.bot:
        # await bot.process_commands(message)
        # be ready to revert :p
        await bot.process_commands(message)
    else:
        return


@bot.event
async def on_command(ctx):
    bot.commands_run += 1
    log = bot.get_channel(445332002942484482)
    em = discord.Embed(color=0xf9e236, title="Command Run!")
    em.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
    em.add_field(name="User ID", value=ctx.author.id)
    em.add_field(name="Server", value=ctx.guild.name)
    em.add_field(name="Server ID", value=ctx.guild.id)
    em.add_field(name="User Status",value=ctx.author.status)
    em.add_field(name="Channel", value=ctx.channel.name)
    em.add_field(name="Command Content", value=f"```{ctx.message.content}```")
    em.set_thumbnail(url=ctx.guild.icon_url)
    await log.send(embed=em)

@bot.event
async def on_message_edit(before, after):
    if before is None or after is None:
        return
    if before.content == after.content:
        return
    if await modlog_check(before.guild.id):
        try:
            lol = bot.get_channel(await get_modlog_channel(before.guild.id))
            em = discord.Embed(color=0x00ff00, title='Message Edited')
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
async def on_reaction_add(reaction, user):
    if reaction.message.author == user:
        return
    if reaction.emoji == '⭐' or reaction.emoji == '🌟':
        x = await bot.db.starboard.find_one({"id": str(user.guild.id)})
        chan = bot.get_channel(x['channel'])
        if not chan:
            return
        emoji_count = reaction.message.reactions[0].count
        if emoji_count > 1:
            em = discord.Embed(color=0xf4bf42, title=f"Stars: {emoji_count}")
            for_description = reaction.message.content
            if not for_description:
                try:
                    for_description = reaction.message.embeds[0].description 
                except:
                    for_description = None
            em.description = for_description or "No content detected."
            em.set_author(name=reaction.message.author.name, icon_url=reaction.message.author.avatar_url)
            try:
                img_url = reaction.message.attachments[0].url
            except IndexError:
                img_url = None
            if not img_url:
                try:
                    img_url = reaction.message.embeds[0].url
                except IndexError:
                    img_url = None
            if img_url:
                em.set_image(url=str(img_url))
            async for x in chan.history(limit=50):
                if x.embeds[0].description == reaction.message.content:
                    await x.edit(embed=em)
                    break
        else:
            x = await bot.db.starboard.find_one({"id": str(user.guild.id)})
            chan = bot.get_channel(x['channel'])
            if not chan:
                return
            try:
                img_url = reaction.message.attachments[0].url
            except IndexError:
                img_url = None
            if not img_url:
                try:
                    img_url = reaction.message.embeds[0].url
                except IndexError:
                    img_url = None
            em = discord.Embed(color=0xf4bf42, title="Stars: 1")
            em.description = reaction.message.content
            em.set_author(name=reaction.message.author.name, icon_url=reaction.message.author.avatar_url)
            if img_url:
                em.set_image(url=str(img_url))
            await chan.send(embed=em)
    else:
        pass
    # with open('data/starmsgs.json') as f:
    #     x = json.loads(f.read())
    # try:
    #     sent = x[str(reaction.message.id)]
    #     with open('data/starboard.json') as f:
    #         a = json.loads(f.read())
    #     try:
    #         channel = bot.get_channel(int(a[str(user.guild.id)]))
    #     except KeyError:
    #         return
    #     msg = await channel.get_message(int(sent))
    #     em = discord.Embed(color=0xf4bf42, title=f"Stars: {len([x for x in reaction.message.reactions if x.emoji == '⭐' or x.emoji == '🌟'])}")
    #     em.description = reaction.message.content
    #     em.set_author(name=reaction.message.author.name, icon_url=reaction.message.author.avatar_url)
    #     await msg.edit(embed=em)
    # except KeyError:

    

        



@bot.event
async def on_guild_join(guild):
    lol = bot.get_channel(392443319684300801)
    em = discord.Embed(color=0xf9e236)
    em.title = "dat banana bot has joined a new server!"
    em.description = f"**{guild.name}**"
    em.add_field(name="Owner", value=str(guild.owner))
    em.add_field(name="Member Count", value=len(guild.members))
    em.set_footer(text=f"ID: {guild.id}")
    em.set_thumbnail(url=guild.icon_url)
    await lol.send(embed=em)
    await guild.channels[0].send(f"Hiya, guys in **{guild.name}**! Thanks for welcoming me! I am dat banana bot, a gud Discord bot. Try me out by typing *help! Here's a rundown of what I can do:\n-Music\n-Starboard\n-Custom Prefix\n-Welcome/Leave/Ban Messages\n-A stack of canvas commands.\n-Statistics for CR, COC and LoL\n\nTo get the most out of me, I do recommend giving me **Administrator** permissions.\n\nHave a nice day! :blush:")

@bot.event
async def on_guild_remove(guild):
    logs_channel = bot.get_channel(392443319684300801)
    em = discord.Embed(color=0xf44242)
    em.title = "dat banana bot has been removed from a server."
    em.description = f"**{guild.name}**"
    em.set_footer(text=f"ID: {guild.id}")
    em.set_thumbnail(url=guild.icon_url)
    await logs_channel.send(embed=em)

    
@bot.event
async def on_member_join(member):
    x = await bot.db.welcome.find_one({"id": str(member.guild.id)})
    if not x:
        return
    channel = int(x['channel'])
    lol = bot.get_channel(channel)
    if not lol:
        return
    await lol.send(x['message'].replace('{name}', member.name).replace('{mention}', member.mention).replace('{members}', str(len(member.guild.members))).replace('{server}', member.guild.name))
    if await modlog_check(member.guild.id):
        lol = bot.get_channel(await get_modlog_channel(member.guild.id))
        em = discord.Embed(color=0x00ff00, title='Member Joined')
        em.add_field(name="Name", value=str(member))
        em.add_field(name='Joined At', value=str(member.joined_at.strftime("%b %m, %Y, %A, %I:%M %p")))
        em.add_field(name="ID", value=member.id)
        em.set_thumbnail(url=member.avatar_url)
        await lol.send(embed=em)
    else:
        pass
    x = await bot.db.autorole.find_one({"id": str(member.guild.id)})
    if x is None:
        return
    rolename = x['role']
    r = discord.utils.get(member.guild.roles, name=rolename)
    await member.add_roles(r)


@bot.event
async def on_member_remove(member):
    x = await bot.db.leave.find_one({"id": str(member.guild.id)})
    if not x:
        return
    channel = int(x['channel'])
    lol = bot.get_channel(channel)
    if not lol:
        return
    await lol.send(x['message'].replace('{name}', member.name).replace('{members}', str(len(member.guild.members))).replace('{server}', member.guild.name))
    if await modlog_check(member.guild.id):
        lol = bot.get_channel(await get_modlog_channel(member.guild.id))
        em = discord.Embed(color=0x00ff00, title='Member Left')
        em.add_field(name="Name", value=str(member))
        em.add_field(name="ID", value=member.id)
        em.set_thumbnail(url=member.avatar_url)
        await lol.send(embed=em)
    else:
        pass


@bot.event
async def on_member_ban(guild, member):
    x = await bot.db.ban.find_one({"id": str(member.guild.id)})
    if not x:
        return
    try:
        channel = int(x['channel'])
    except KeyError:
        return
    if channel is False:
        pass
    else:
        lol = bot.get_channel(channel)
        if lol is None:
            return
        await lol.send(x['message'].replace('{name}', member.name).replace('{members}', str(len(member.guild.members))).replace('{server}', member.guild.name))
    if await modlog_check(member.guild.id):
        lol = bot.get_channel(await get_modlog_channel(member.guild.id))
        em = discord.Embed(color=0x00ff00, title='Member Banned')
        em.add_field(name="Name", value=str(member))
        em.add_field(name="ID", value=member.id)
        em.add_field(name="Server", value=guild.name)
        em.set_thumbnail(url=member.avatar_url)
        await lol.send(embed=em)
    else:
        pass



@bot.event
async def on_message_delete(message):
    if message is None:
        return
    if await modlog_check(message.guild.id):
        try:
            try:
                img_url = message.attachments[0].url
            except IndexError:
                img_url = None
            if not img_url:
                try:
                    img_url = message.embeds[0].url
                except IndexError:
                    img_url = None
            lol = bot.get_channel(await get_modlog_channel(message.guild.id))
            em = discord.Embed(color=0x00ff00, title='Message Deleted')
            em.add_field(name='Content', value=message.content if message.content else "Embed")
            em.add_field(name='Sent By', value=str(message.author))
            em.add_field(name='Channel', value=f"<#{message.channel.id}>")
            if img_url:
                em.set_image(url=img_url)
            await lol.send(embed=em)
        except KeyError:
            pass
    else:
        pass




@bot.event
async def on_command_error(ctx, error):
    em = discord.Embed(color=0xf44e42, title='An error occurred.')
    missing_param_errors = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError)
    if isinstance(error, missing_param_errors):
        em = discord.Embed(color=0xf44242, title="Incorrect Usage of Command!")
        em.description = f"This is the correct usage:\n**{ctx.prefix}{ctx.command.signature}**"
        return await ctx.send(embed=em)
    if isinstance(error, commands.NotOwner):
        em.description = 'Not my daddy! This command is for the owner only.'
        return await ctx.send(embed=em)
    elif isinstance(error, commands.MissingPermissions):
        missing = ""
        perms = {
            "ban_members": "Ban Members",
            "kick_members": "Kick Members",
            "manage_messages": "Manage Messages",
            "manage_emojis": "Manage Emojis",
            "administrator": "Administrator",
            "manage_guild": "Manage Server"
        }
        for x in error.missing_perms:
            missing += f"{perms[x]} \n"
        em.description = f'{bot.get_emoji(430853687754358788)} Uh-oh, not enough permissions! You are missing the following permissions required to run this command:\n\n{missing}'
        return await ctx.send(embed=em)
    elif isinstance(error, commands.CommandOnCooldown):
        retry_time = error.retry_after
        if retry_time < 60:
            actual_time = f"{int(retry_time)} seconds"
        elif retry_time >= 60 and retry_time < 3600:
            actual_time = f"{int(retry_time / 60)} minutes"
        elif retry_time >= 3600 and retry_time < 86400:
            actual_time = f"{int(retry_time / 3600)} hours"
        elif retry_time >= 86400:
            actual_time = f"{int(retry_time / 86400)} days"
        em.description = f'ACK. The command is on cooldown! You can use it again in **{actual_time}**.'
        return await ctx.send(embed=em)
    elif isinstance(error, commands.NoPrivateMessage):
        em.description = "This command can only be used in a server. Get out of our DMs! \n(╯°□°）╯︵ ┻━┻"
        return await ctx.send(embed=em)
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        logger.error(error)

            
            
@bot.command()
@commands.is_owner()
async def presence(ctx, Type=None, *, thing=None):
    """What AM I doing?!?!?!"""
    if Type is None:
        await ctx.send('Do it right, plox! Usage: *presence [game/stream] [msg]')
    else:
      if Type.lower() == 'stream':
        await bot.change_presence(activity=discord.Game(name=thing,type=1, url='https://www.twitch.tv/a'), status='online')
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
async def say(ctx, *, message: commands.clean_content()):
    '''I say what you want me to say. Oh boi...'''
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    finally:
        await ctx.send(message)                   
                       

@bot.command()
async def ping(ctx):
    """Premium ping pong giving you a websocket latency."""
    color = 0xf9e236
    e = discord.Embed(color=color, title='Pinging')
    e.description = 'Please wait... :ping_pong:'
    msg = await ctx.send(embed=e)
    em = discord.Embed(color=color, title='PoIIIng! Your supersonic latency is:')
    em.description = f"{bot.latency * 1000:.4f} ms"
    em.set_thumbnail(url="https://media.giphy.com/media/3ornjZwtv8PoahqgOA/giphy.gif")
    await msg.edit(embed=em)
  
        
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
        'src': inspect.getsource,
        'session': bot.session
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
