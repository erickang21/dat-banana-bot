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
from utils.stopwatch import Stopwatch
from utils.type import Type
from contextlib import redirect_stdout
from discord.ext import commands
import json
import ezjson
import colorama
from box import Box
from motor.motor_asyncio import AsyncIOMotorClient
from ext.context import DatContext
from ext.logger import Logger as logger
from cogs.utils.utils import Utils

colorama.init()

with open("data/apikeys.json") as f:
    x = json.load(f)

db = AsyncIOMotorClient(x["mongodb"])


async def getprefix(bot, message):
    if isinstance(message.channel, discord.DMChannel): return "*"
    x = await db.datbananabot.prefix.find_one({ "id": str(message.guild.id) })
    pre = x['prefix'] if x is not None else '*'
    return commands.when_mentioned_or(pre)(bot, message)


bot = commands.Bot(command_prefix=getprefix, owner_id=277981712989028353, case_insensitive=True)
bot._last_result = None
bot.session = aiohttp.ClientSession(loop=bot.loop)
bot.starttime = time.time()
bot.commands_run = 0
bot.logger = logger
bot.config = Box(x)
bot.edits = {}
bot.bulkDeletes = {}
bot.snipes = {}
bot.editsnipes = {}
utils = Utils(bot)
with open("data/apikeys.json") as f:
    x = json.load(f)
bot.db = db.datbananabot
cogs = [ "cogs." + x.replace(".py", "") for x in os.listdir("cogs") if x.endswith(".py") ]
bot.remove_command("help")

for cog in cogs:
    try:
        bot.load_extension(cog)
    except Exception as e:
        bot.logger.error(e)


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


async def get_prefix_as_str(message):
    if isinstance(message.channel, discord.DMChannel): return "*"
    x = await bot.db.prefix.find_one({ "id": str(message.guild.id) })
    pre = x['prefix'] if x is not None else '*'
    return pre

async def process_commands(message):
    ctx = await bot.get_context(message, cls=DatContext)
    if not ctx.command:
        return
    await bot.invoke(ctx)

async def modlog_check(guildid):
    x = await bot.db.modlog.find_one({'id': str(guildid)})
    if not x:
        return False
    return True


async def get_modlog_channel(guildid):
    x = await bot.db.modlog.find_one({'id': str(guildid)})
    return int(x['channel'])

# A task to clean edits to free memory
async def _sweeper():
    while True:
        bot.edits = {}
        await asyncio.sleep(60 * 60) # 1 Hour

# A task to clean up the bots last bulk deletes
async def _sweep_bulk_deletes():
    while True:
        bot.bulkDeletes = {}
        await asyncio.sleep(60) # 1 Minute

@bot.event
async def on_ready():
    if bot.user.id != 388476336777461770:
        print("COPYING ALERT! COULD NOT IDENTIFY BOT USER! EXPOSED!")
        exit() # :p
    bot.loop.create_task(_sweeper())
    bot.loop.create_task(_sweep_bulk_deletes())
    with open("restart.txt") as f:
        x = f.readlines()
    stuff = [f.strip("\n") for f in x]

    msg = await bot.get_channel(int(stuff[0])).get_message(int(stuff[1]))
    await msg.edit(content="Successfully restarted, and READY TO ROLL! :white_check_mark:")
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
        "*help | Music officially fixed! YEET",
        "*help | Bananaes < Leagye"
    ]
    print('Bot is online, and ready to ROLL!')
    while True:
        await bot.change_presence(activity=discord.Game(name=random.choice(presence)))
        await asyncio.sleep(20)


@bot.event
async def on_message(message):
    prefix = await get_prefix_as_str(message)
    x = await bot.db.blacklist.find_one({"id": message.author.id})
    if not x or not x.get("status", False):
        pass
    else:
        return
    data = await bot.db.afk.find_one({"id": message.author.id})
    if data:
        if data.get("status", None):
            await bot.db.afk.update_one({"id": message.author.id}, {"$set": {"status": False}})
            await message.channel.send(f"Oh hey {message.author.mention}, welcome back! For your convenience I cleared your AFK status.")
    if re.match(f"^<@!?{bot.user.id}>$", message.content):
        msg = f"""
{bot.get_emoji(505725404695232512)} **What's poppin?**

You pinged dat zero two bot, and that *should* be me, so I answered.

__Features__
:star: Starboard
:wave: Welcome/leave/ban messages
{bot.get_emoji(493575154241110021)} Moderation
{bot.get_emoji(356789385875816448)} Fun
:pencil: Image Manipulation
:video_game: Game Stats for Clash Royale, Clash of Clans, and League of Legends
{bot.get_emoji(469456375882448896)} Utility
:musical_note: Music (Might be broken)
:spy: Snipe and Editsnipe. Nowhere to hide!
:pencil2: Customize me by disabling commands you want.
:moneybag: Per-server economy that can be disabled/enabled according to your needs.
:rofl: Memes. Memes. The stuff of life.

And so much more. 

My prefix for this server is set to `{prefix}`. Run the `{prefix}prefix` command to change it! Also, don't forget to check out all my commands using `{prefix}help`.

Have a gucci day! {bot.get_emoji(485250850659500044)}
        """
        await message.channel.send(msg)
    if re.findall(r"(http(s)://|)(discord\.gg|discord\.io|discordapp\.com/invite)\S+", message.content):
        if message.author.guild_permissions.manage_guild or message.author.guild_permissions.administrator or message.author.id == message.guild.owner.id:
            pass
        if message.author.id == bot.user.id:
            pass
        else:           
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
                    em = discord.Embed(color=0xf9e236, title="Invite Posted")
                    em.description = textwrap.dedent(f"""
{bot.get_emoji(430340802879946773)} Sent by **{str(message.author)}**

:hash: In channel {message.channel.mention}

:link: Link:
{message.content}

                    """)
                    em.timestamp = message.created_at
                    await lol.send(embed=em)
                except KeyError:
                    pass
    # levelup = await bot.db.level.find_one({"id": message.guild.id})
    # if levelup:
    #     try:
    #         match = levelup['data'][str(message.author.id)]
    #         if match is False: # match could be 0 which returns false, and i don't want that
    #             pass 
    #     except KeyError:
    #         pass 
    #     match += 1
    #     await bot.db.level.update_one({"id": message.guild.id}, {"$set": {"data": match}}, upsert = True)
    #     if match % 20 == 0:
    #         await message.channel.send(f"Woo-hoo, {message.author.mention}! You hit level {match / 20}! Keep talkin' for more!")
    if message.mentions:
        for x in message.mentions:
            data = await bot.db.afk.find_one({"id": x.id})
            if not data:
                pass
            elif not data['status']:
                pass
            elif data:
                await message.channel.send(f"Hush, don't ping **{x.name}**. He's AFK right now, doing this: **{data['status']}**.")
            else:
                continue
    if not message.author.bot:
        blacklistcmds = await bot.db.blacklistcmd.find_one({"id": message.guild.id})
        ctx = await bot.get_context(message, cls=DatContext)
        if not blacklistcmds or not blacklistcmds['cmds']:
            
            await bot.invoke(ctx)
        else:
            prefix = await get_prefix_as_str(message)
            if message.content.startswith(prefix) and message.content.strip(prefix).split(" ")[0].lower() in blacklistcmds['cmds']:
                return await ctx.send("OOF! Looks like this command is disabled. Can't do anything then. (Except send this message, of course.)")
            else:
                message.content = message.content.replace("\u200b", "")
                ctx = await bot.get_context(message, cls=DatContext)
                await bot.invoke(ctx)
                #await bot.process_commands(message)


# REACTION ROLE EVENTS

@bot.event
async def on_raw_reaction_add(payload):
    data = await bot.db.reactionrole.find_one({"id": payload.guild_id})
    if not data: 
        return

    # Data from the DB
    data = Box(data)
    # Data from event
    guild = bot.get_guild(payload.guild_id)
    channel = bot.get_channel(payload.channel_id)
    message = await channel.get_message(payload.message_id)
    member = guild.get_member(payload.user_id)
    emoji = payload.emoji

    # Check if the channel + message are equal to the one saved
    if data.channel_id == payload.channel_id and data.message_id == payload.message_id:
        try:
            role_id = data.data[str(emoji.id)]
        except KeyError:
            return # Don't continue if the role ain't there
        role = discord.utils.get(guild.roles, id=role_id)
        if not role:
            return # Don't add a role that doesn't exist
        
        # Add the damn role
        await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    data = await bot.db.reactionrole.find_one({"id": payload.guild_id})
    if not data: 
        return

    # Data from the DB
    data = Box(data)
    # Data from event
    guild = bot.get_guild(payload.guild_id)
    channel = bot.get_channel(payload.channel_id)
    message = await channel.get_message(payload.message_id)
    member = guild.get_member(payload.user_id)
    emoji = payload.emoji

    # Check if the channel + message are equal to the one saved
    if data.channel_id == payload.channel_id and data.message_id == payload.message_id:
        try:
            role_id = data.data[str(emoji.id)]
        except KeyError:
            return # Don't continue if the role ain't there
        role = discord.utils.get(guild.roles, id=role_id)
        if not role:
            return # Don't remove a role that doesn't exist
        
        # Remove the damn role
        await member.remove_roles(role)

        

    

@bot.event #stalker
async def on_command(ctx):
    bot.commands_run += 1
    #log = bot.get_channel(445332002942484482)
    #em = discord.Embed(color=discord.Color(value=0xf9e236), title="Command Run!")
    #em.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
    #em.add_field(name="User ID", value=ctx.author.id)
    #em.add_field(name="Server", value=ctx.guild.name)#    em.add_field(name="Server ID", value=ctx.guild.id)
    #em.add_field(name="Channel", value=ctx.channel.name)
    #em.add_field(name="Command Content", value=f"```{ctx.message.content}```")
    #em.set_thumbnail(url=ctx.guild.icon_url)
    #await log.send(embed=em)

                                           
@bot.event
async def on_message_edit(before, after):
    if before is None or after is None:
        return
    try:
        snipes = bot.editsnipes[str(before.channel.id)]
    except:
        snipes = bot.editsnipes[str(before.channel.id)] = []
    data = {
        "before": before.content or before.embeds[0].description,
        "author": before.author,
        "after": after.content or after.embeds[0].description,
        "before_message": before,
        "after_message": after
    }
    if len(snipes) >= 10: snipes.remove(snipes[-1])
    snipes.insert(0, data)
    pre = await get_prefix_as_str(after)
    if after.content.startswith(pre):
        ctx = await bot.get_context(after, cls=DatContext)
        await bot.invoke(ctx)
    if before.content == after.content:
        return
    if await modlog_check(before.guild.id):
        try:
            lol = bot.get_channel(await get_modlog_channel(before.guild.id))
            em = discord.Embed(color=discord.Color(value=0xf9e236), title="Message Edited")
            em.description = textwrap.dedent(f"""
{bot.get_emoji(430340802879946773)} Sent by **{str(before.author)}**

:hash: In channel {before.channel.mention}

:page_facing_up: **Before:**
{before.content}

:page_with_curl: **After:**
{after.content}
            """)
            em.timestamp = before.created_at
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
        em = discord.Embed(color=discord.Color(value=0xf4bf42), title=f"Starred Message")
            
        display = f"""
{reaction.emoji} **Stars:** {emoji_count}
:1234: **ID:** {reaction.message.id}
:link: **Link:** Click [here]({reaction.message.jump_url}) (mobile only).
-------------------------
{reaction.message.content}
        """
        em.description = display
        em.set_footer(text=reaction.message.author.name, icon_url=reaction.message.author.avatar_url)
        em.timestamp = datetime.datetime.utcnow()
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
        if emoji_count > 1:
            
            
            async for x in chan.history(limit=50):
                if reaction.message.content in x.embeds[0].description and x.author.id == bot.user.id:
                    await x.edit(embed=em)
                    break
        else:
            x = await bot.db.starboard.find_one({"id": str(user.guild.id)})
            chan = bot.get_channel(x['channel'])
            if not chan:
                return
            await chan.send(embed=em)
    else:
        pass


@bot.event
async def on_reaction_remove(reaction, user):
    if reaction.emoji == '⭐' or reaction.emoji == '🌟':
        x = await bot.db.starboard.find_one({"id": str(user.guild.id)})
        chan = bot.get_channel(x['channel'])
        if not chan:
            return
        try:
            emoji_count = reaction.message.reactions[0].count
        except IndexError:
            async for x in chan.history(limit=50):
                if x.embeds[0].description == reaction.message.content:
                    return await x.delete()
        if not emoji_count:
            async for x in chan.history(limit=50):
                if x.embeds[0].description == reaction.message.content:
                    return await x.delete()
        if emoji_count >= 1:
            em = discord.Embed(color=discord.Color(value=0xf4bf42), title=f"Stars: {emoji_count}")
            em.description = reaction.message.content
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
        elif emoji_count == 0:
            async for x in chan.history(limit=50):
                if x.embeds[0].description == reaction.message.content:
                    await x.delete()
                    break


@bot.event
async def on_guild_join(guild):
    await bot.db.economy.update_one({"id": guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
    lol = bot.get_channel(392443319684300801)
    em = discord.Embed(color=discord.Color(value=0xf9e236))
    em.title = "dat banana bot has joined a new server!"
    em.description = f"**{guild.name}**"
    em.add_field(name="Owner", value=str(guild.owner))
    em.add_field(name="Member Count", value=len(guild.members))
    em.set_footer(text=f"ID: {guild.id}")
    em.set_thumbnail(url=guild.icon_url)
    await lol.send(embed=em)
    msg = f"""
What's poppin', lovely citizens in **{guild.name}**?

I'm **dat zero two bot**, a lovely bot with everything you ever need out of a Discord bot.

In fact, I'm so lovely, I'll introduce myself right now.

__Features__
:star: Starboard
:wave: Welcome/leave/ban messages
{bot.get_emoji(493575154241110021)} Moderation
{bot.get_emoji(356789385875816448)} Fun
:pencil: Image Manipulation
:video_game: Game Stats for Clash Royale, Clash of Clans, and League of Legends
{bot.get_emoji(469456375882448896)} Utility
:musical_note: Music (Might be broken)
:spy: Snipe and Editsnipe. Nowhere to hide!
:pencil2: Customize me by disabling commands you want.
:moneybag: Per-server economy that can be disabled/enabled according to your needs.
:rofl: Memes. Memes. The stuff of life.

Lastly, don't forget to join the bot's support server for...support, and for chilling!

https://discord.gg/3Nxb7yZ

Have a gucci day! {bot.get_emoji(485250850659500044)}
    """

    for x in guild.channels:
        try:
            await x.send(msg)
            break
        except:
            continue

@bot.event
async def on_guild_remove(guild):
    logs_channel = bot.get_channel(392443319684300801)
    em = discord.Embed(color=discord.Color(value=0xf44242))
    em.title = "dat banana bot has been removed from a server."
    em.description = f"**{guild.name}**"
    em.add_field(name="Owner", value=str(guild.owner))                                       
    em.set_footer(text=f"ID: {guild.id}")
    em.set_thumbnail(url=guild.icon_url)
    await logs_channel.send(embed=em)

    
@bot.event
async def on_member_join(member):
    # MEMBER COUNTER
    data = await bot.db.membercounter.find_one({"id": member.guild.id})
    if not data: pass
    else:
        try:
            total = data['total']
            humans = data['humans']
            bots = data['bots']
            await bot.get_channel(total).edit(name=f"Total: {len(member.guild.members)}")
            if member.bot:
                await bot.get_channel(bots).edit(name=f"Bots: {len([x for x in member.guild.members if x.bot])}")
            else:
                await bot.get_channel(humans).edit(name=f"Humans: {len([x for x in member.guild.members if not x.bot])}")
        except:
            pass
    # WELCOME
    x = await bot.db.welcome.find_one({ "id": str(member.guild.id) })
    if not x:
        return
    channel = int(x['channel'])
    lol = bot.get_channel(channel)
    if not lol:
        return
    await lol.send(x['message'].replace('{name}', member.name).replace('{mention}', member.mention).replace('{members}', str(len(member.guild.members))).replace('{server}', member.guild.name))
    if await modlog_check(member.guild.id):
        lol = bot.get_channel(await get_modlog_channel(member.guild.id))
        em = discord.Embed(color=discord.Color(value=0xf9e236), title='Member Joined')
        em.description = textwrap.dedent(f"""
{bot.get_emoji(430340802879946773)} User: {str(member)}

:1234: User ID: {member.id}

:house_with_garden: Server: {member.guild.name}    

:clock10: Joined at: {str(member.joined_at.strftime("%A, %b %m, %Y at %I:%M %p"))}    
        """)
        em.set_thumbnail(url=member.avatar_url)
        em.timestamp = datetime.datetime.utcnow()
        await lol.send(embed=em)
    else:
        pass

    # AUTOROLE 
    x = await bot.db.autorole.find_one({ "id": str(member.guild.id) })
    if x is None:
        return
    rolename = x['role']
    r = discord.utils.get(member.guild.roles, name=rolename)
    if r: # role could possibily be deleted.
        await member.add_roles(r)

    # LEVEL-UP (NOT IN USE)
    levelup = await bot.db.level.find_one({"id": member.guild.id})
    if levelup:
        try:
            match = levelup['data']
            if match is False:  # match could be 0 which returns false, and I don't want that
                return
        except KeyError:
            return
        match[str(member.id)] = 0
        await bot.db.level.update_one({"id": member.guild.id}, {"$set": {"data": match}}, upsert=True)



@bot.event
async def on_member_remove(member):
    # MEMBER COUNTER
    data = await bot.db.membercounter.find_one({"id": member.guild.id})
    if not data: pass
    else:
        try:
            total = data['total']
            humans = data['humans']
            bots = data['bots']
            await bot.get_channel(total).edit(name=f"Total: {len(member.guild.members)}")
            if member.bot:
                await bot.get_channel(bots).edit(name=f"Bots: {len([x for x in member.guild.members if x.bot])}")
            else:
                await bot.get_channel(humans).edit(name=f"Humans: {len([x for x in member.guild.members if not x.bot])}")
        except:
            pass
        
    x = await bot.db.leave.find_one({ "id": str(member.guild.id) })
    if not x:
        return
    channel = int(x['channel'])
    lol = bot.get_channel(channel)
    if not lol:
        return
    await lol.send(x['message'].replace('{name}', member.name).replace('{members}', str(len(member.guild.members))).replace('{server}', member.guild.name))
    if await modlog_check(member.guild.id):
        lol = bot.get_channel(await get_modlog_channel(member.guild.id))
        em = discord.Embed(color=discord.Color(value=0xf44e42), title='Member Left')
        em.description = textwrap.dedent(f"""
{bot.get_emoji(430340802879946773)} User: {str(member)}

:1234: User ID: {member.id}

:house_with_garden: Server: {member.guild.name}        
        """)
        em.timestamp = datetime.datetime.utcnow()
        em.set_thumbnail(url=member.avatar_url)
        await lol.send(embed=em)


@bot.event
async def on_member_ban(guild, member):
    x = await bot.db.ban.find_one({ "id": str(member.guild.id) })
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
        if not lol:
            return
        await lol.send(x['message'].replace('{name}', member.name).replace('{members}', str(len(member.guild.members))).replace('{server}', member.guild.name))
    if await modlog_check(member.guild.id):
        lol = bot.get_channel(await get_modlog_channel(member.guild.id))
        em = discord.Embed(color=discord.Color(value=0xf44e42), title='Member Banned')
        em.description = textwrap.dedent(f"""
{bot.get_emoji(430340802879946773)} Banned User: {str(member)}

:1234: Banned User ID: {member.id}

:house_with_garden: Server: {guild.name}        
        """)
        em.timestamp = datetime.datetime.utcnow()
        em.set_thumbnail(url=member.avatar_url)
        await lol.send(embed=em)


@bot.event
async def on_raw_bulk_message_delete(payload):
    bot.bulkDeletes[bot.get_channel(payload.channel_id).guild.id] = True
    if await modlog_check(payload.guild_id):
        lol = bot.get_channel(await get_modlog_channel(payload.guild_id))
        em = discord.Embed(color=discord.Color(value=0xf44e42), title='Messages Purged')
        em.description = textwrap.dedent(f"""
:hash: Channel: {bot.get_channel(payload.channel_id).mention}

:newspaper: Messages Deleted: {len(payload.message_ids)}      
        """)
        em.timestamp = datetime.datetime.utcnow()
        await lol.send(embed=em)

@bot.event
async def on_message_delete(message):
    if message is None:
        return
    try:
        snipes = bot.snipes[str(message.channel.id)]
    except:
        snipes = bot.snipes[str(message.channel.id)] = []
    data = {
        "content": message.content or message.embeds[0].description,
        "author": message.author,
        "message": message
    }
    if len(snipes) >= 10: snipes.remove(snipes[-1])
    snipes.insert(0, data)
    if await modlog_check(message.guild.id):
        if bot.bulkDeletes.get(message.guild.id):
            return
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
            em = discord.Embed(color=discord.Color(value=0xf9e236), title="Message Deleted")
            em.description = textwrap.dedent(f"""
{bot.get_emoji(430340802879946773)} Sent by **{str(message.author)}**

:hash: In channel {message.channel.mention}

:page_facing_up: **Content:**
{message.content}

            """)
            em.timestamp = message.created_at
            if img_url:
                em.set_image(url=img_url)
            await lol.send(embed=em)
        except KeyError:
            pass


@bot.event
async def on_command_error(ctx, error):
    em = discord.Embed(color=discord.Color(value=0xf44e42), title='An error occurred.')
    missing_param_errors = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError)
    if isinstance(error, missing_param_errors):
        em = discord.Embed(color=discord.Color(value=0xf44242), title="Incorrect Usage of Command!")
        em.description = f"This is the correct usage:\n**{ctx.prefix}{ctx.command.signature}**"
        return await ctx.send(embed=em)
    if isinstance(error, commands.NotOwner):
        em.description = 'Not my daddy! This command is for the owner only.'
        return await ctx.send(embed=em)
    elif isinstance(error, commands.MissingPermissions):
        missing = ""
        for x in error.missing_perms:
            missing += f"{utils.capitalize(x)} \n"
        
        return await ctx.send(f"{bot.get_emoji(506168446174887956)} You don't have permission to run this command! Maybe try getting these permissions:\n\n{missing}", edit=False)
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

        return await ctx.send(f"BAKA! You're using this command too fast. Don't make me repeat myself, and wait for **{actual_time}**.", edit=False)
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        log = bot.get_channel(445332002942484482)
        traceback_text = "\n".join(traceback.format_exception(type(error), error, error.__traceback__, 10))
        await ctx.send("NANI?! An unexpected error occurred when trying to run the command. You did nothing wrong. Let me show this to my senpai and hope that he fixes it. Meanwhile, join the support server and see what's poppin'! \n\nhttps://discord.gg/3Nxb7yZ", edit=False)
        embed = discord.Embed(color=discord.Color(value=0xf44e42), title="Error Report")
        embed.set_author(name=f"{str(ctx.author)} (ID: {ctx.author.id})", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Server", value=ctx.guild.name)
        embed.add_field(name="Server ID", value=ctx.guild.id)
        embed.add_field(name="Channel", value=ctx.channel.name)
        embed.add_field(name="Command Content", value=ctx.message.content)
        embed.description = f"**Full Traceback:**\n\n```{traceback_text}```"
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await log.send(bot.get_user(277981712989028353).mention, embed=embed)
        logger.error(error)

            
            
@bot.command(hidden=True) # because no one uses this xd
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
    color = discord.Color(value=0xf9e236)
    e = discord.Embed(color=color, title='Pinging')
    e.description = 'Please wait... :ping_pong:'
    msg = await ctx.send(embed=e)
    em = discord.Embed(color=color, title='PoIIIng! Your supersonic latency is:')
    em.description = f"{bot.latency * 1000:.4f} ms"
    em.set_thumbnail(
        url="https://media.giphy.com/media/nE8wBpOIfKJKE/giphy.gif")
    await msg.edit(embed=em)
  
        
@bot.command()
async def invite(ctx):
    """Allow my bot to join the hood. YOUR hood."""
    await ctx.send("Lemme join that hood -> https://discordapp.com/oauth2/authorize?client_id=388476336777461770&scope=bot&permissions=2146958591")                       

                       
@bot.command(name='discord')
async def _discord(ctx):
    """We have an awesome hood to join, join now!"""
    await ctx.send("Your turn to join the hood -> https://discord.gg/wvkVknA")

def paginate(text: str):
    """Simple generator that paginates text."""
    last = 0
    pages = []
    for curr in range(0, len(text)):
        if curr % 1970 == 0:
            pages.append(text[last:curr])
            last = curr
            appd_index = curr
    if appd_index != len(text) - 1:
        pages.append(text[last:curr])
    return list(filter(lambda a: a != "", pages))

@bot.command(name="eval", aliases=["ev"])
async def _eval(ctx, *, code: str):
    if not dev_check(ctx.author.id):
        return await ctx.send("This command is for the developers only!")
    env = {
        "bot": bot,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message,
        "msg": ctx.message,
        "_": bot._last_result,
        "source": inspect.getsource,
        "src": inspect.getsource,
        "session": bot.session,
        "docs": lambda x: print(x.__doc__)
    }

    env.update(globals())
    body = cleanup_code(code)
    stdout = io.StringIO()
    err = out = None
    to_compile = f"async def func():\n{textwrap.indent(body, '  ')}"
    stopwatch = Stopwatch().start()

    try:
        exec(to_compile, env)
    except Exception as e:
        stopwatch.stop()
        err = await ctx.send(f"**Error**```py\n{e.__class__.__name__}: {e}\n```\n**Type**```ts\n{Type(e)}```\n⏱ {stopwatch}")
        return await ctx.message.add_reaction("\u2049")

    func = env["func"]
    stopwatch.restart()
    try:
        with redirect_stdout(stdout):
            ret = await func()
            stopwatch.stop()
    except Exception as e:
        stopwatch.stop()
        value = stdout.getvalue()
        err = await ctx.send(f"**Error**```py\n{value}{traceback.format_exc()}\n```\n**Type**```ts\n{Type(err)}```\n⏱ {stopwatch}")
    else:
        value = stdout.getvalue()
        if ret is None:
            if value:
                try:
                    out = await ctx.send(f"**Output**```py\n{value}```\n⏱ {stopwatch}")
                except:
                    paginated_text = paginate(value)
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f"```py\n{page}\n```", edit=False)
                            break
                        await ctx.send(f"```py\n{page}\n```", edit=False)
                    await ctx.send(f"⏱ {stopwatch}", edit=False)
        else:
            bot._last_result = ret
            try:
                out = await ctx.send(f"**Output**```py\n{value}{ret}```\n**Type**```ts\n{Type(ret)}```\n⏱ {stopwatch}")
            except:
                paginated_text = paginate(f"{value}{ret}")
                for page in paginated_text:
                    if page == paginated_text[-1]:
                        out = await ctx.send(f"```py\n{page}```", edit=False)
                        break
                    await ctx.send(f"```py\n{page}```", edit=False)
                await ctx.send(f"**Type**```ts\n{Type(ret)}```\n⏱ {stopwatch}", edit=False)
        if out:
            await ctx.message.add_reaction("\u2705")
        elif err:
            await ctx.message.add_reaction("\u2049")
        else:
            await ctx.message.add_reaction("\u2705")                  
                       
with open("data/apikeys.json") as f:
    x = json.loads(f.read())
try:
    bot.run(x['bottoken'])
except Exception as e:
    print("Could not start the bot. Check the token.")
