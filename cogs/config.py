import discord
import sys
import os
import io
import re
import asyncio
import json
import ezjson
import textwrap
from discord.ext import commands
from .utils.utils import Utils


class Config:
    def __init__(self, bot):
        self.bot = bot
        self.utils = Utils(bot)
    
    @commands.command(aliases=['reactrole', 'rroles'])
    async def reactionroles(self, ctx):
        """Set up reaction roles for your server."""
        await ctx.send("Welcome to the interactive setup for reaction roles!\n\nLet's get started. Remember, type `cancel` at any time to exit the process.", edit=False)
        await ctx.send("Which channel do you want me to send the reaction role messages in? Make sure I have permissions to send messages there! (Timing out in 60 seconds)", edit=False)
        repeat1 = True
        while repeat1:
            x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
            if x.content == "cancel": return await ctx.send("I have cancelled the process. Until next time!", edit=False)
            chan = self.utils.format_channel(x.content)
            if not chan:
                await ctx.send("This channel doesn't exist.")
            if not chan.permissions_for(ctx.guild.me).send_messages:
                await ctx.send("I don't have permissions to send messages in that channel! Let's try that again.", edit=False)
            else:
                repeat1 = False
        
        await ctx.send("Awesome! Let's continue." , edit=False)
        repeat2 = True
        counter = 0
        data = {}
        while repeat2:
            await ctx.send("Enter the emoji to use. This emoji will show up on the menu and will be used as the reaction emoji. **Please note, only custom emojis are supported.**")
            x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
            #default_emoji_match = r":[a-zA-Z]+:"
            custom_emoji_match = r"<:[a-zA-Z]+:[0-9]+>"
            if re.match(custom_emoji_match, x.content):
                emoji_id = int(re.findall(r"[0-9]+", x.content)[0])
                emoji = self.bot.get_emoji(emoji_id)
                if not emoji:
                    await ctx.send("Invalid emoji.")
                await ctx.send(f"This has been detected as a **custom emoji.** If it appears correctly here, it should display correctly in the message: {x.content}\n\nIf you are unsatisfied, you can type `skip` **on the next prompt**, to ignore this entry.", edit=False)
                await ctx.send("Please enter the name of the role to assign the emoji to. Enter `skip` to skip this emoji and re-enter one.", edit=False)
                x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                if x.content.lower() == "skip":
                    pass
                elif x.content.lower() == "cancel":
                    repeat2 = False
                    return await ctx.send("I have cancelled the process. Until next time!", edit=False)
                else:
                    role_name = x.content
                    if not discord.utils.get(ctx.guild.roles, name=role_name):
                        await ctx.send("Invalid role name. Please try again.", edit=False)
                    else:
                        counter += 1
                        data[str(emoji_id)] = role_name
                        await ctx.send(f"Alright, added that emoji + role pair! Type `next` to continue adding more roles (You are at {counter}/10 roles) or `end` to end and prepare the message.", edit=False)
                        x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                        if x.content.lower() == "next":
                            pass
                        elif x.content.lower() == "end":
                            await ctx.send("Alright, getting things finished for you...", edit=False)
                            em = discord.Embed(color=ctx.author.color, name="Reaction Roles")
                            desc = """
Welcome to the interactive reaction role system.

Setting up your roles is simple! React below to the emoji and the bot will give you the corresponding role.

**__Roles__**\n\n"""
                            for x in data:
                                desc += f"{self.bot.get_emoji(int(x))} {data[x]}\n"
                            em.description = desc
                            await chan.send(embed=em)
            elif x.content.lower() == "cancel":
                repeat2 = False
                return await ctx.send("I have cancelled the process. Until next time!", edit=False)
            else:
                await ctx.send("Invalid emoji.", edit=False)




    @commands.command(aliases=['conf'])
    async def config(self, ctx):
        """Show my configuration on your server."""
        antilink = await self.bot.db.antilink.find_one({"id": ctx.guild.id})
        autorole = await self.bot.db.autorole.find_one({"id": str(ctx.guild.id)})
        ban = await self.bot.db.ban.find_one({"id": str(ctx.guild.id)})
        blacklistcmd = await self.bot.db.blacklistcmd.find_one({"id": ctx.guild.id})
        economy = await self.bot.db.economy.find_one({"id": ctx.guild.id})
        leave = await self.bot.db.leave.find_one({"id": str(ctx.guild.id)})
        economy = await self.bot.db.economy.find_one({"id": ctx.guild.id})
        modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
        prefix = await self.bot.db.prefix.find_one({"id": str(ctx.guild.id)})
        starboard = await self.bot.db.starboard.find_one({"id": str(ctx.guild.id)})
        welcome = await self.bot.db.welcome.find_one({"id": str(ctx.guild.id)})
        conf = ""
        conf += f"""
This is my configuration for this server (**{ctx.guild.name}**). 
Note that this only shows the config, but does not support editing it.\n
        """

        if not antilink:
            conf += "**Antilink**\nStatus: **Disabled**\n\n"
        elif not antilink.get("status", ""):
            conf += "**Antilink**\nStatus: **Disabled**\n\n"
        else:
            conf += "**Antilink**\nStatus: **Enabled**\n\n"

        if not autorole:
            conf += "**Autorole**\nStatus: **Disabled**\n\n"
        if not autorole.get("role"):
            conf += "**Autorole**\nStatus: **Disabled**\n\n"
        else:
            conf += f"**Autorole**\nStatus: **Enabled**\nRole: **{autorole.get('role')}**\n\n"

        if not blacklistcmd:
            conf += "**Disabled Commands**\nCommands: **None**\n\n"
        else:
            conf += f"**Disabled Commands**\nCommands: {', '.join(blacklistcmd.get('cmds')) if blacklistcmd.get('cmds') else 'None'}\n\n"

        if not economy.get("registered"):
            conf += "**Economy**\nStatus: **Disabled**\n\n"
        else:
            conf += f"**Economy**\nStatus: **Enabled**\nRegistered Members: **{len(economy.get('users'))}**\n\n"

        if not modlog:
            conf += "**Mod Logs**\nStatus: **Disabled**\n\n"
        if not modlog.get("channel"):
            conf += "**Mod Logs**\nStatus: **Disabled**\n\n"
        else:
            conf += f"**Mod Logs**\nStatus: **Enabled**\nChannel: <#{modlog.get('channel')}>\n\n"
        
        if not prefix:
            conf += "**Prefix**\nPrefix: `*`\n\n"
        if not prefix.get("prefix"):
            conf += "**Prefix**\nPrefix: `*`\n\n"
        else:
            conf += f"**Prefix**\nPrefix: `{prefix.get('prefix')}`\n\n"

        if not starboard:
            conf += "**Starboard**\nStatus: **Disabled**\n\n"
        if not starboard.get("channel"):
            conf += "**Starboard**\nStatus: **Disabled**\n\n"
        else:
            conf += f"**Starboard**\nStatus: **Enabled**\nChannel: <#{starboard.get('channel')}>\n\n"

        conf += "__Messages__\n\n"

        if not welcome:
            conf += "**Welcome**\nStatus: **Disabled**\n\n"
        if not welcome.get("channel"):
            conf += "**Welcome**\nStatus: **Disabled**\n\n"
        else:
            conf += f"**Welcome**\nStatus: **Enabled**\nChannel: <#{welcome.get('channel')}>\nMessage: {welcome.get('message')}\n\n"
        
        if not leave:
            conf += "**Leave**\nStatus: **Disabled**\n\n"
        if not leave.get("channel"):
            conf += "**Leave**\nStatus: **Disabled**\n\n"
        else:
            conf += f"**Leave**\nStatus: **Enabled**\nChannel: <#{leave.get('channel')}>\nMessage: {leave.get('message')}\n\n"

        if not ban:
            conf += "**Ban**\nStatus: **Disabled**\n\n"
        if not ban.get("channel"):
            conf += "**Ban**\nStatus: **Disabled**\n\n"
        else:
            conf += f"**Ban**\nStatus: **Enabled**\nChannel: <#{ban.get('channel')}>\nMessage: {ban.get('message')}\n\n"

        em = discord.Embed(color=ctx.author.color, title="Guild Configuration")
        em.description = conf
        await ctx.send(embed=em)

        

    @commands.command(aliases=['blcmd', 'disablecmd'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def blacklistcmd(self, ctx, action=None, cmd=None):
        """Blacklist a command for the server."""
        if not cmd and not action:
            blacklist = await self.bot.db.blacklistcmd.find_one({"id": ctx.guild.id})
            if not blacklist or not blacklist['cmds']:
                await self.bot.db.blacklistcmd.update_one({"id": ctx.guild.id}, {"$set": {"cmds": []}}, upsert=True)
                the_cmds = "No commands blacklisted!"
            else:
                the_cmds = "\n".join(blacklist["cmds"])
            the_cmds += "\n\nTo add a command to the blacklist, use *blacklistcmd add [cmd name].\nTo remove a command from the blacklist, use *blacklist remove [cmd name]."
            em = discord.Embed(color=ctx.author.color, title="Blacklisted Commands")
            em.description = the_cmds
            return await ctx.send(embed=em)
        if (action and not cmd) or (action and cmd == "help"):
            bcmd_help = """
****Blacklistcmd Help**__

This command disables a command for the server. It can also show disabled commands and re-enable a command.
Note that you cannot disable this command. 
An alias for this is *disablecmd.

*blacklistcmd: Show the list of disabled commands.
*blacklistcmd help: Shows this message.
*blacklistcmd add [cmd]: Disables the command for the server.
*blacklistcmd remove [cmd]: Enables the command for the server.
            """
            return await ctx.send(bcmd_help)
        elif action == "add" and cmd:
            if cmd == "blacklistcmd":
                return await ctx.send("You can't blacklist this command!")
            c = self.bot.get_command(cmd)
            if not c:
                return await ctx.send("That command doesn't exist.")
            blacklist = await self.bot.db.blacklistcmd.find_one({"id": ctx.guild.id})
            if not blacklist or not blacklist['cmds']:
                await self.bot.db.blacklistcmd.update_one({"id": ctx.guild.id}, {"$set": {"cmds": [cmd]}}, upsert=True)
            else:
                new_cmds = blacklist['cmds']
                new_cmds.append(cmd)
                await self.bot.db.blacklistcmd.update_one({"id": ctx.guild.id}, {"$set": {"cmds": new_cmds}}, upsert=True)
            return await ctx.send(f"The command **{cmd}** was added to the blacklist. :white_check_mark:")
        elif action == "remove" and cmd:
            if cmd == "blacklistcmd":
                return await ctx.send("You can't blacklist this command!")
            c = self.bot.get_command(cmd)
            if not c:
                return await ctx.send("That command doesn't exist.")
            blacklist = await self.bot.db.blacklistcmd.find_one({"id": ctx.guild.id})
            if not blacklist or not blacklist['cmds']:
                return await ctx.send("You haven't blacklisted any commands!")
            if cmd not in blacklist['cmds']:
                return await ctx.send("This command isn't blacklisted! Why remove it... :thinking:")
            new_cmds = blacklist['cmds']
            new_cmds.remove(cmd)
            await self.bot.db.blacklistcmd.update_one({"id": ctx.guild.id}, {"$set": {"cmds": new_cmds}}, upsert=True)
            return await ctx.send(f"The command **{cmd}** was removed from the blacklist. :white_check_mark:")


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def starboard(self, ctx, *, action=None):
        """Turn on a starboard for the server that is for STARS!"""
        starboard_help = """
**__Starboard Help__**
Starboard creates a channel (or you can set to an existing one) that basically records this server's best messages. If you see a great message, react to it with :star: or :star2: and it will send to the specified channel.
Think of it as a server-wide pins channel.

*starboard -> Creates a new channel and turns on starboard in that channel.
*starboard reset -> In case you manually deleted the starboard channel and need to re-create a new one.
*starboard disable -> Disable the starboard for the given channel. Note that this no longer deletes the channel.
*starboard set [channel] -> Turn on the starboard in an existing channel by mentioning it.
*starboard help -> Show this.
        """
        if action is None:
            x = await self.bot.db.starboard.find_one({'id': str(ctx.guild.id)})
            if x is not None:
                return await ctx.send(f"A starboard for this server has already been created. If the channel was deleted, use *starboard reset to re-create it.")
            else:
                msg = await ctx.send("One sec, building the awesome starboard with :star:s")
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(send_messages = False),
                    ctx.guild.me: discord.PermissionOverwrite(send_messages = True)
                }
                try:
                    channel = await ctx.guild.create_text_channel('starboard', overwrites=overwrites)
                except Exception as e:
                    return await ctx.send(f"An unexpected error occurred. Details: \n```{e}```")
                await self.bot.db.starboard.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": channel.id}}, upsert=True)
                return await msg.edit(content=f"Woo-hoo, created {channel.mention} for you to star-t :star:-ing now!")
        elif action.lower() == 'reset':
            msg = await ctx.send("One sec, building the awesome starboard with :star:s")
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(send_messages = False),
                ctx.guild.me: discord.PermissionOverwrite(send_messages = True)
            }
            channel = await ctx.guild.create_text_channel('starboard', overwrites=overwrites)
            await self.bot.db.starboard.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": channel.id}}, upsert=True)
            return await msg.edit(content=f"Woo-hoo, created {channel.mention} for you to star-t :star:-ing now!")
        elif action.lower() == 'disable':
            msg = await ctx.send("Disabling the :star:board of awesomeness...")

            await self.bot.db.starboard.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": False}}, upsert=True)
            return await msg.edit(content='Successfully disabled the starboard. :cry:')
        elif action.lower().startswith("set"):
            channel_regex = r"^\<#\d+\>$"
            print(int(action.strip("set ").strip("<#").strip(">")))
            if re.match(channel_regex, action.strip("set ")):
                action = int(action.strip("set ").strip("<#").strip(">"))
                chan = self.bot.get_channel(action)
                if not chan:
                    return await ctx.send("You've got an invalid channel there!")
                await self.bot.db.starboard.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": int(action)}}, upsert=True)
                return await ctx.send(f"Alright! I set the starboard to {chan.mention}. Have fun :)")
            else:
                return await ctx.send("Looks like that's an invalid channel. Go for *starboard help if you need help.")
        elif action.lower() == "help":
            return await ctx.send(starboard_help)
        else:
            return await ctx.send(starboard_help)


    @commands.command(aliases=['welcome', 'wm'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def welcomemsg(self, ctx, action=None):
        if action is None:
            em = discord.Embed(color=0x00ff00, title='Welcome Messages')
            try:
                x = await self.bot.db.welcome.find_one({"id": str(ctx.guild.id)})
                if x['channel'] is False:
                    em.description = 'Welcome messages are disabled for this server.'
                else:
                    em.description = f"Welcome messages are turned on for this server, set in <#{x['channel']}>.\n\nMessage: {x['message']}"
            except KeyError:
                em.description = 'Welcome messages are disabled for this server.'
            await ctx.send(embed=em)
        else:
            if action.lower() == 'on':
                await ctx.send("Please mention the channel to set welcome messages in.", edit=False)
                try:
                    x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                except asyncio.TimeoutError:
                    return await ctx.send("Request timed out. Please try again.", edit=False)
                if not x.content.startswith("<#") and not x.content.endswith(">"):
                    return await ctx.send("Please properly mention the channel.", edit=False)
                channel = x.content.strip("<#").strip(">")
                try:
                    channel = int(channel)
                except ValueError:
                    return await ctx.send("Did you properly mention a channel? Probably not.", edit=False)
                await ctx.send("Please enter the message to send when someone joins.\n\n```Variables: \n{name}: The user's name.\n{mention}: Mention the user.\n{members}: The amount of members currently in the server.\n{server}: The name of the server.```", edit=False)
                try:
                    x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                except asyncio.TimeoutError:
                    return await ctx.send("Request timed out. Please try again.")
                await self.bot.db.welcome.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": channel, "message": x.content}}, upsert=True)
                await ctx.send("Successfully turned on welcome messages for this guild.", edit=False)
                modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
                if modlog:
                    em = discord.Embed(color=discord.Color(value=0x00ff00), title="Welcome Messages Enabled")
                    em.description = textwrap.dedent(f"""
                    {self.bot.get_emoji(430340802879946773)} By **{str(ctx.author)}**

                    :house_with_garden: Server: {ctx.guild.name} 

                    :hash: Channel: <#{channel}>

                    :speech_balloon: Message:
                    {x.content}
                    """)
            
                    channel = self.bot.get_channel(int(modlog['channel']))
                    if channel:
                        await channel.send(embed=em)
            elif action.lower() == 'off':
                await self.bot.db.welcome.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": False, "message": None}}, upsert=True)
                await ctx.send("Successfully turned off welcome messages for this guild.")
                modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
                if modlog:
                    em = discord.Embed(color=discord.Color(value=0x00ff00), title="Welcome Messages Disabled")
                    em.description = textwrap.dedent(f"""
                    {self.bot.get_emoji(430340802879946773)} By **{str(ctx.author)}**

                    :house_with_garden: Server: {ctx.guild.name} 
                    """)
                    channel = self.bot.get_channel(int(modlog['channel']))
                    if channel:
                        await channel.send(embed=em)
    @commands.command(aliases=['leave'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def leavemsg(self, ctx, action=None):
        if action is None:
            em = discord.Embed(color=0x00ff00, title='Leave Messages')
            try:
                x = await self.bot.db.leave.find_one({"id": str(ctx.guild.id)})
                if x['channel'] is False:
                    em.description = 'Leave messages are disabled for this server.'
                else:
                    em.description = f"Leave messages are turned on for this server, set in <#{x['channel']}>.\n\nMessage: {x['message']}"
            except KeyError:
                em.description = 'Leave messages are disabled for this server.'
            await ctx.send(embed=em)
        else:
            if action.lower() == 'on':
                
                await ctx.send("Please mention the channel to set leave messages in.", edit=False)
                try:
                    x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                except asyncio.TimeoutError:
                    return await ctx.send("Request timed out. Please try again.")
                if not x.content.startswith("<#") and not x.content.endswith(">"):
                    return await ctx.send("Please properly mention the channel.")
                channel = x.content.strip("<#").strip(">")
                try:
                    channel = int(channel)
                except ValueError:
                    return await ctx.send("Did you properly mention a channel? Probably not.")
                await ctx.send("Please enter the message to send when someone leaves.\n\n```Variables: \n{name}: The user's name.\n{members}: The amount of members currently in the server.\n{server}: The name of the server.```", edit=False)
                try:
                    x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                except asyncio.TimeoutError:
                    return await ctx.send("Request timed out. Please try again.")
                await self.bot.db.leave.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": channel, "message": x.content}}, upsert=True)
                await ctx.send("Successfully turned on leave messages for this guild.", edit=False)
                modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
                if modlog:
                    em = discord.Embed(color=discord.Color(value=0x00ff00), title="Leave Messages Enabled")
                    em.description = textwrap.dedent(f"""
                    {self.bot.get_emoji(430340802879946773)} By **{str(ctx.author)}**

                    :house_with_garden: Server: {ctx.guild.name} 

                    :hash: Channel: <#{channel}>

                    :speech_balloon: Message:
                    {x.content}
                    """)
                    channel = self.bot.get_channel(int(modlog['channel']))
                    if channel:
                        await channel.send(embed=em)
            elif action.lower() == 'off':
                await self.bot.db.leave.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": False, "message": None}}, upsert=True)
                await ctx.send("Successfully turned off leave messages for this guild.")
                modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
                if modlog:
                    em = discord.Embed(color=discord.Color(
                        value=0x00ff00), title="Leave Messages Disabled")
                    em.description = textwrap.dedent(f"""
                    {self.bot.get_emoji(430340802879946773)} By **{str(ctx.author)}**

                    :house_with_garden: Server: {ctx.guild.name} 
                    """)
                    channel = self.bot.get_channel(int(modlog['channel']))
                    if channel:
                        await channel.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def banmsg(self, ctx, action=None):
        if action is None:
            em = discord.Embed(color=0x00ff00, title='Leave Messages')
            try:
                x = await self.bot.db.ban.find_one({"id": str(ctx.guild.id)})
                if x['channel'] is False:
                    em.description = 'Ban messages are disabled for this server.'
                else:
                    em.description = f"Ban messages are turned on for this server, set in <#{x['channel']}>.\n\nMessage: {x['message']}"
            except KeyError:
                em.description = 'Ban messages are disabled for this server.'
            await ctx.send(embed=em)
        else:
            if action.lower() == 'on':
                await ctx.send("Please mention the channel to set ban messages in.")
                try:
                    x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                except asyncio.TimeoutError:
                    return await ctx.send("Request timed out. Please try again.")
                if not x.content.startswith("<#") and not x.content.endswith(">"):
                    return await ctx.send("Please properly mention the channel.")
                channel = x.content.strip("<#").strip(">")
                try:
                    channel = int(channel)
                except ValueError:
                    return await ctx.send("Did you properly mention a channel? Probably not.")
                await ctx.send("Please enter the message to send when someone gets banned.\n\n```Variables: \n{name}: The user's name.\n{members}: The amount of members currently in the server.\n{server}: The name of the server.```")
                try:
                    x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                except asyncio.TimeoutError:
                    return await ctx.send("Request timed out. Please try again.")
                await self.bot.db.ban.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": channel, "message": x.content}}, upsert=True)
                await ctx.send("Successfully turned on ban messages for this guild.")
                modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
                if modlog:
                    em = discord.Embed(color=discord.Color(
                        value=0x00ff00), title="Ban Messages Enabled")
                    em.description = textwrap.dedent(f"""
                    {self.bot.get_emoji(430340802879946773)} By **{str(ctx.author)}**

                    :house_with_garden: Server: {ctx.guild.name} 

                    :hash: Channel: <#{channel}>

                    :speech_balloon: Message:
                    {x.content}
                    """)
                    channel = self.bot.get_channel(int(modlog['channel']))
                    if channel:
                        await channel.send(embed=em)
            elif action.lower() == 'off':
                await self.bot.db.ban.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": False, "message": None}}, upsert=True)
                await ctx.send("Successfully turned off ban messages for this guild.")
                modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
                if modlog:
                    em = discord.Embed(color=discord.Color(
                        value=0x00ff00), title="Ban Messages Disabled")
                    em.description = textwrap.dedent(f"""
                    {self.bot.get_emoji(430340802879946773)} By **{str(ctx.author)}**

                    :house_with_garden: Server: {ctx.guild.name} 
                    """)
                    channel = self.bot.get_channel(int(modlog['channel']))
                    if channel:
                        await channel.send(embed=em)
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
    async def autorole(self, ctx, *, role):
        """Sets the bot to automatically give a role on a member's join."""
        if role.lower() == 'off':
            await self.bot.db.autorole.update_one({"id": str(ctx.guild.id)}, {"$set": {"role": False}}, upsert=True)
            await ctx.send(f"Disabled autoroles for this server.")
            modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
            if modlog:
                em = discord.Embed(color=discord.Color(value=0x00ff00), title="Autorole Disabled")
                em.description = textwrap.dedent(f"""
                {self.bot.get_emoji(430340802879946773)} By **{str(ctx.author)}**  
                
                :house_with_garden: Server: {ctx.guild.name}   
                """)
                channel = self.bot.get_channel(int(modlog['channel']))
                if channel:
                    await channel.send(embed=em)
        else:
            r = discord.utils.get(ctx.guild.roles, name=str(role))
            if r is None:
                return await ctx.send("Role not found in the server. Note that roles muts be entered case sensitive.")
            r = await Utils.clean_text(ctx, str(r))
            await self.bot.db.autorole.update_one({"id": str(ctx.guild.id)}, {"$set": {"role": str(r)}}, upsert=True)
            await ctx.send(f"Successfully enabled an autorole for the role: **{str(r)}**.")
            modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
            if modlog:
                em = discord.Embed(color=discord.Color(
                    value=0x00ff00), title="Autorole Enabled")
                em.description = textwrap.dedent(f"""
                {self.bot.get_emoji(430340802879946773)} By **{str(ctx.author)}**
                
                :house_with_garden: Server: {ctx.guild.name} 

                :bust_in_silhouette: Role: {str(r)}
                """)
                channel = self.bot.get_channel(int(modlog['channel']))
                if channel:
                    await channel.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def modlog(self, ctx, action=None):
        if action is None:
            x = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
            em = discord.Embed(color=0x00ff00, title="Mod Log Status")
            em.description = f"Mod logs are enabled in this server, in <#{x['channel']}>."
            if x is None:
                em.description = 'Mod logs are turned off for this server.'
            return await ctx.send(embed=em)
        if action.lower() == 'on':
            await ctx.send("Please mention the channel for mod logs to be sent in.")
            try:
                x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
            except asyncio.TimeoutError:
                return await ctx.send("Request timed out. Please try again.")
            if not x.content.startswith("<#") and not x.content.endswith(">"):
                return await ctx.send("Please properly mention the channel.")
            channel = x.content.strip("<#").strip(">")
            try:
                channel = int(channel)
            except ValueError:
                return await ctx.send("Did you properly mention a channel? Probably not.")
            await self.bot.db.modlog.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": channel}}, upsert=True)
            await ctx.send(f"Successfully turned on Mod Logs in <#{channel}>. Enjoy! :white_check_mark:")
            modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
            channel = self.bot.get_channel(int(modlog['channel']))
            em = discord.Embed(color=discord.Color(value=0x00ff00), title="Modlogs Enabled")
            em.description = textwrap.dedent(f"""
            {self.bot.get_emoji(468607258440237066)} Enabled by: {str(ctx.author)}
            :zipper_mouth: User: {str(ctx.author)}

            :hash: Channel: {channel.mention}
            """)
            if channel:
                return await channel.send(embed=em)
        if action.lower() == 'off':
            modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
            channel = self.bot.get_channel(int(modlog['channel']))
            em = discord.Embed(color=discord.Color(value=0x00ff00), title="Modlogs Disabled")
            em.description = textwrap.dedent(f"""
            {self.bot.get_emoji(468607258440237066)} Disabled by: {str(ctx.author)}
            """)
            if channel:
                await channel.send(embed=em)
            await self.bot.db.modlog.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": False}}, upsert=True)
            return await ctx.send("Turned off Mod Logs. Whew...")
        else:
            return await ctx.send("That ain't an action. Please enter either `on` or `off`.")


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def prefix(self, ctx, prefix=None):
        em = discord.Embed(color=0xf9e236, title="Bot Prefix")
        if prefix is None:
            em.description = f"The bot's prefix for server **{ctx.guild.name}** is set to `{ctx.prefix}`."
            return await ctx.send(embed=em)
        if prefix.lower() == 'clear':
            await self.bot.db.prefix.update_one({"id": str(ctx.guild.id)}, {"$set": {"prefix": "*"}}, upsert=True)
            em.description = f"The bot's prefix is now set to the default: `*`."
            await ctx.send(embed=em)
            modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
            if modlog:
                channel = self.bot.get_channel(int(modlog['channel']))
                em = discord.Embed(color=discord.Color(value=0x00ff00), title="Prefix Changed")
                em.description = textwrap.dedent(f"""
                {self.bot.get_emoji(430340802879946773)} Changed by: {str(ctx.author)}
                
                :symbols: New Prefix: `*`
                """)
                if channel:
                    await channel.send(embed=em)
        else:
            await self.bot.db.prefix.update_one({"id": str(ctx.guild.id)}, {"$set": {"prefix": prefix}}, upsert=True)
            em.description = f"The bot's prefix for this server is set to: `{prefix}`."
            await ctx.send(embed=em)
            modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
            if modlog:
                channel = self.bot.get_channel(int(modlog['channel']))
                em = discord.Embed(color=discord.Color(
                    value=0x00ff00), title="Prefix Changed")
                em.description = textwrap.dedent(f"""
                {self.bot.get_emoji(430340802879946773)} Changed by: {str(ctx.author)}
                
                :symbols: New Prefix: `{prefix}`
                """)
                if channel:
                    await channel.send(embed=em)


def setup(bot): 
    bot.add_cog(Config(bot)) 

