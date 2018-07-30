import discord
import sys
import os
import io
import asyncio
import json
import ezjson
import textwrap
from discord.ext import commands


class mod:
    def __init__(self, bot):
        self.bot = bot


    # @commands.command()
    # @commands.guild_only()
    # @commands.has_permissions(manage_guild = True)
    # async def reactionrole(self, ctx, action):
    #     if action.lower() == 'on':
    #         data = []
    #         roles = []
    #         for x in range(20):
    #             await ctx.send("Let's get started! First off, which role would you like to give?")
    #             try:
    #                 x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
    #             except asyncio.TimeoutError:
    #                 return await ctx.send("Timed out. Oof.")
    #             role = discord.utils.get(ctx.guild.roles, name=x.content)
    #             if not role:
    #                 return await ctx.send("Invalid role name. Must be case-sensitive!")
    #             roles.append(str(role))
    #             await ctx.send("Which emoji would you like to assign it with? (Enter the **custom emoji's ID**, and make sure I have access to it.)")  
    #             try:
    #                 x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
    #             except asyncio.TimeoutError:
    #                 return await ctx.send("Timed out. Oof.")
    #             emoji = self.bot.get_emoji(int(x.content))
    #             if not emoji:
    #                 return await ctx.send("Invalid emoji.")
    #             await ctx.send("Mention the channel to send the reaction messages in.")
    #             try:
    #                 x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
    #             except asyncio.TimeoutError:
    #                 return await ctx.send("Timed out. Oof.")
    #             if not x.content.startswith("<#") and not x.content.endswith(">"):
    #                 return await ctx.send("Invalid channel mention.")
    #             channel = x.content.strip("<#").strip(">")
    #             try:
    #                 channel = int(channel)
    #             except ValueError:
    #                 return await ctx.send("Invalid channel mention.")
    #             await ctx.send("Done! Now, you can reply 'continue' to add another role to the list or 'stop' to end it. You can also do 'cancel' to forget all that we did before.")
    #             try:
    #                 x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
    #             except asyncio.TimeoutError:
    #                 return await ctx.send("Timed out. Oof.")
    #             if x.content.lower() == 'continue':
    #                 await ctx.send("Carrying on! :ok_hand:")
    #                 continue
    #             elif x.content.lower() == 'stop':
    #                 stuff = {
    #                     "role": role,
    #                     "emoji": emoji,
    #                     "channel": channel
    #                 }
    #                 msg = ""
    #                 a = [x['role']]
                    
    #                 data.append(stuff)
                    
                    
    #                 await self.bot.db.reactionrole.update_one({"id": ctx.guild.id}, {"$set": {"data": data}})
    #                 await ctx.send("Saved, locked and loaded, and ready to ROLL!")
    #     elif action.lower() == 'off':
    #         await self.bot.db.antilink.update_one({"id": ctx.guild.id}, {"$set": {"status": False}})
    #         await ctx.send("Antilink disabled. Advertising continues.")
    #     else:
    #         return await ctx.send("Reactionrole command:\n*reactionrole [on/off]")
   

    @commands.command(aliases=['blacklist'])
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
    async def antilink(self, ctx, action):
        """Prevents people from sending invite links in the channel."""
        if action.lower() == 'on':
            if not ctx.guild.me.guild_permissions.manage_messages:
                return await ctx.send("I do not have the **Manage Messages** permission. This means I cannot delete links!")
            await self.bot.db.antilink.update_one({"id": ctx.guild.id}, {"$set": {"status": True}}, upsert=True)
            await ctx.send("Antilink is enabled. Put an end to advertising.")
        elif action.lower() == 'off':
            await self.bot.db.antilink.update_one({"id": ctx.guild.id}, {"$set": {"status": False}})
            await ctx.send("Antilink disabled. Advertising continues.")
        else:
            return await ctx.send("Antilink command:\n*antilink [on/off]")


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def lockdown(self, ctx, action):
        """Prevents anyone from chatting in the current channel."""
        if action.lower() == 'on':
            msg = await ctx.send("Locking down the channel...")
            for x in ctx.guild.members:
                await ctx.channel.set_permissions(x, send_messages=False)
            return await msg.edit(content="The channel has been successfully locked down. :lock: ")
        elif action.lower() == 'off':
            msg = await ctx.send("Unlocking the channel...")
            for x in ctx.guild.members:
                await ctx.channel.set_permissions(x, send_messages=True)
            return await msg.edit(content="The channel has been successfully unlocked. :unlock: ")
        else:
            return await ctx.send("Lockdown command:\n*lockdown [on/off]")



    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def starboard(self, ctx, action=None):
        """Turn on a starboard for the server that is for STARS!"""
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
        elif action.lower() == 'delete':
            msg = await ctx.send("Deleting the :star:board of awesomeness...")
            with open("data/starboard.json") as f:
                x = json.loads(f.read())
            try:
                channel = self.bot.get_channel(x[str(ctx.guild.id)])
            except KeyError:
                return await ctx.send(f"A starboard for this server was never created. Why delete something that doesn't exist? {self.bot.get_emoji(430853715059277863)}")
            try:
                await channel.delete()
            except:
                await self.bot.db.starboard.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": False}}, upsert=True)
                return await msg.edit(content="Starboard is disabled, but I was unable to delete the channel.")
            await self.bot.db.starboard.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": False}}, upsert=True)
            return await msg.edit(content='Successfully removed the starboard. :cry:')
        else:
            return await ctx.send("Unknown action. Either leave blank, use *starboard reset to re-create a deleted channel, or *starboard delete to remove the server's starboard.")

        
    # @commands.command()
    # @commands.guild_only()
    # @commands.has_permissions(administrator = True)
    # async def dm(self, ctx, user: discord.Member, *, msg: str):
    #     """Escort your DM to someone thru the bot. Usage: *dm [tag person] [msg]"""
    #     try:
    #         em = discord.Embed(color=ctx.author.color, title="New Message")
    #         em.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
    #         em.description = msg
    #         em.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
    #         await user.send(embed=em)
    #         await ctx.message.delete()            
    #         await ctx.send("SuccESS! Your DM has made it! :white_check_mark: ")
    #     except commands.MissingPermissions:
    #         await ctx.send("Aw, come on! You thought you could get away with DM'ing people without permissions.")
    #     except:
    #         await ctx.send("Error :x:. Make sure your message is shaped in this way: *dm [tag person] [msg]")


    
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def warn(self, ctx, user: discord.Member, *, reason: str):
        """It's time to stop. Sends that warning. Usage: *warn [tag person] [reason]"""
        try:
            color = 0xf44242
            em = discord.Embed(color=color, title=f"WARNING: by {ctx.message.author.name} from **{ctx.author.guild.name}**.", description=f"{reason}")
            await user.send(embed=em)
            await ctx.message.delete()
            await ctx.send("User has been DM'd :white_check_mark:. Pray that the user is a gud boi now. :pray:")
        except:
            await ctx.send("Something happened and the DM could not make it :x:. The user could be blocking DMs from the server, or you did not use the format correctly. Usage: *warn [tag person] [reason].")    
       
    
    @commands.command(aliases=['clean'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages = True)
    async def purge(self, ctx, num: int, from_user: discord.Member = None):
        """Deletes a # of msgs. *purge [# of msgs].""" 
        try:
            float(num)
        except ValueError:
            return await ctx.send("The number is invalid. Make sure it is valid! Usage: *purge [number of msgs]")
        try:
            if not from_user:
                await ctx.channel.purge(limit=num+1, bulk=True)
            else:
                await ctx.channel.purge(limit=num+1, bulk=True, check=lambda x: x.author.id == from_user.id)
            msg = await ctx.send("Purged successfully :white_check_mark:", delete_after=3)
        except discord.Forbidden:
            await ctx.send("Purge unsuccessful. The bot does not have Manage Msgs permission.")

    
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        """Kicks a member into the world outside your server."""
        if user.id == ctx.author.id:
            return await ctx.send("I don't understand your logic. Kicking yourself?")
        try:
            await user.kick(reason=reason)
            color = 0xf9e236
            em = discord.Embed(color=color, title='Kicked!')
            em.add_field(name='User', value=user.name)
            em.add_field(name='Kicked By', value=ctx.author.name)
            if reason is None:
                reason = 'No reason given.'
            else:
                reason = reason
            em.add_field(name='Reason', value=reason)
            em.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=em)
        except discord.Forbidden:
            await ctx.send("Oops! I don't have enough permissions to use the boot.")
        
        
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        """Swings the mighty Ban Hammer on that bad boy."""
        if user.id == ctx.author.id:
            return await ctx.send("I don't understand your logic. Using the ban hammer on yourself?")
        try:
            await user.ban(reason=reason)
            color = 0xf9e236
            em = discord.Embed(color=color, title='Banned!')
            em.description = f'The ban hammer has fell down. {self.bot.get_emoji(436342184330002442)}'
            em.add_field(name='User', value=user.name)
            em.add_field(name='Banned By', value=ctx.author.name)
            reason = reason if reason is not None else 'No reason given.'
            em.add_field(name='Reason', value=reason)
            em.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=em)
        except discord.Forbidden:
            await ctx.send("Oops! I don't have enough permissions to swing this ban hammer.")



    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def mute(self, ctx, user: discord.Member, mutetime=None, *, reason=None):
        '''Forces someone to shut up. Usage: *mute [user] [time in mins]'''
        modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
        if modlog:
            em = discord.Embed(color=discord.Color(value=0x00ff00), title="Member was muted.")
            em.description = textwrap.dedent(f"""
            :zipper_mouth: User: {str(user)}

            {self.bot.get_emoji(430340802879946773)} Muted by: {str(ctx.author)}

            :1234: User ID: {user.id}

            :timer: Timer: {f"{str(mutetime)} minutes" if mutetime else "No time limit."}

            :hash: Type: Channel
            """)
            
            channel = self.bot.get_channel(int(modlog['channel']))
            if channel:
                await channel.send(embed=em)
        try:
            await ctx.channel.set_permissions(user, send_messages=False)
            await ctx.channel.send(f"{user.mention} is now forced to shut up. :zipper_mouth: ")
            if mutetime:
                try:
                    mutetime =int(mutetime)
                    mutetime = mutetime * 60
                except ValueError:
                    return await ctx.send("Your time is an invalid number. Make sure...it is a number.")               
                await asyncio.sleep(mutetime)
                await ctx.channel.set_permissions(user, send_messages=True)
                await ctx.channel.send(f"{user.mention} is now un-shutted up.")
        except discord.Forbidden:
            return await ctx.send("I could not mute the user. Make sure I have the manage channels permission.")
        except commands.errors.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with shutting someone up without permissions.")


    @commands.command(aliases=['sm'])
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def servermute(self, ctx, user: discord.Member = None):
        '''Forces someone to shut up through the entire server. OUCH.'''
        if user is None:
            await ctx.send("Bruh. Tag a user to mute them...")
        else:
                    modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
        if modlog:
            em = discord.Embed(color=discord.Color(
                value=0x00ff00), title="Member was muted.")
            em.description = textwrap.dedent(f"""
            :zipper_mouth: User: {str(user)}

            {self.bot.get_emoji(430340802879946773)} Muted by: {str(ctx.author)}

            :1234: User ID: {user.id}

            :hash: Type: Server
            """)

            channel = self.bot.get_channel(int(modlog['channel']))
            if channel:
                await channel.send(embed=em)
            msg = await ctx.send("Muting user...")
            role = discord.utils.get(ctx.guild.roles, name='Muted')
            if not role:
                try:
                    role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(permissions=1024)) 
                    await role.edit(position=ctx.guild.me.roles[-1].position - 1)
                except discord.Forbidden:
                    return await msg.edit(content="Don't have enough permissions. For flawless bot functions, give the Administrator permission to the bot.")
            await user.add_roles(role)
            for x in ctx.guild.channels:
                await x.set_permissions(role, send_messages=False)
            await msg.edit(content="The user has been muted for this server. :zipper_mouth:")


    @commands.command(aliases=['sum'])
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def serverunmute(self, ctx, user: discord.Member = None):
        '''Un-shuts someone up from the entire server. YEEE.'''
        if user is None:
            await ctx.send("Bruh. Tag a user to unmute them...")
        else:
                    modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
        if modlog:
            em = discord.Embed(color=discord.Color(
                value=0x00ff00), title="Member was unmuted.")
            em.description = textwrap.dedent(f"""
            :zipper_mouth: User: {str(user)}

            {self.bot.get_emoji(430340802879946773)} Unmuted by: {str(ctx.author)}

            :1234: User ID: {user.id}

            :house_with_garden: Type: Server
            """)

            channel = self.bot.get_channel(int(modlog['channel']))
            if channel:
                await channel.send(embed=em)
            msg = await ctx.send("Unmuting user...")
            try:
                await user.remove_roles("Muted")
            except discord.Forbidden:
                return await ctx.send("Uh-oh! Not enough permissions!")
            await msg.edit(content="The user has been unmuted for this server. :grin:")



    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unmute(self, ctx, user: discord.Member):
        '''Allows someone to un-shut up. Usage: *unmute [user]'''
        modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
        if modlog:
            em = discord.Embed(color=discord.Color(
                value=0x00ff00), title="Member was unmuted.")
            em.description = textwrap.dedent(f"""
            :zipper_mouth: User: {str(user)}

            {self.bot.get_emoji(430340802879946773)} Unuted by: {str(ctx.author)}

            :1234: User ID: {user.id}

            :hash: Type: Channel
            """)

            channel = self.bot.get_channel(int(modlog['channel']))
            if channel:
                await channel.send(embed=em)
        try:
            await ctx.channel.set_permissions(user, send_messages=True)
            await ctx.channel.send(f"{user.mention} is now un-shutted up.")
        except discord.Forbidden:
            await ctx.send("Couldn't unmute the user. Uh-oh...")
        except commands.errors.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with shutting someone up without permissions.")              
    

    @commands.command(aliases=['arole'])
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
    async def addrole(self, ctx, user: discord.Member, *, role):
        """Adds a role to a user."""
        r = discord.utils.get(ctx.guild.roles, name=str(role))
        if r is None:
            return await ctx.send("Role not found. Please note that roles are case sensitive!")
        if r.name in [x.name for x in user.roles]:
            return await ctx.send(f"Looks like **{str(user)}** already has the role **{role}**.")
        try:
            await user.add_roles(r)
            return await ctx.send(f"Success! **{str(user)}** has been given the role **{role}**.")
        except discord.Forbidden:
            return await ctx.send("Bot does not have enough permissions to give roles.")
        
        
        
        
    @commands.command(aliases=['rrole'])
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
    async def removerole(self, ctx, user: discord.Member, *, role):
        """Removes a role from a user."""
        r = discord.utils.get(ctx.guild.roles, name=str(role))
        if r is None:
            return await ctx.send("Role not found. Please note that roles are case sensitive!")
        if r.name not in [x.name for x in user.roles]:
            return await ctx.send(f"Looks like **{str(user)}** never had the role **{role}**.")
        try:
            await user.remove_roles(r)
            return await ctx.send(f"Success! **{str(user)}** has been removed from the role **{role}**.")
        except discord.Forbidden:
            return await ctx.send("Bot does not have enough permissions to remove role.")
        


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
                await ctx.send("Please mention the channel to set welcome messages in.")
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
                await ctx.send("Please enter the message to send when someone joins.\n\n```Variables: \n{name}: The user's name.\n{mention}: Mention the user.\n{members}: The amount of members currently in the server.\n{server}: The name of the server.```")
                try:
                    x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                except asyncio.TimeoutError:
                    return await ctx.send("Request timed out. Please try again.")
                await self.bot.db.welcome.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": channel, "message": x.content}}, upsert=True)
                await ctx.send("Successfully turned on welcome messages for this guild.")
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
                
                await ctx.send("Please mention the channel to set leave messages in.")
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
                await ctx.send("Please enter the message to send when someone leaves.\n\n```Variables: \n{name}: The user's name.\n{members}: The amount of members currently in the server.\n{server}: The name of the server.```")
                try:
                    x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                except asyncio.TimeoutError:
                    return await ctx.send("Request timed out. Please try again.")
                await self.bot.db.leave.update_one({"id": str(ctx.guild.id)}, {"$set": {"channel": channel, "message": x.content}}, upsert=True)
                await ctx.send("Successfully turned on leave messages for this guild.")
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

                    :hash: Channel: <#{channel}>

                    :speech_balloon: Message:
                    {x.content}
                    """)
    
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
        else:
            r = discord.utils.get(ctx.guild.roles, name=str(role))
            if r is None:
                return await ctx.send("Role not found in the server. Note that roles muts be entered case sensitive.")
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
            ezjson.dump("data/modlog.json", ctx.guild.id, channel)
            return await ctx.send(f"Successfully turned on Mod Logs in <#{channel}>. Enjoy! :white_check_mark:")
        if action.lower() == 'off':
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
            return await ctx.send(embed=em)
        else:
            await self.bot.db.prefix.update_one({"id": str(ctx.guild.id)}, {"$set": {"prefix": prefix}}, upsert=True)
            em.description = f"The bot's prefix for this server is set to: `{prefix}`."
            return await ctx.send(embed=em)
        
            
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def hackban(self, ctx, id, reason=None):
        try:
            id = int(id)
        except ValueError:
            return await ctx.send("Did you enter a valid user ID?")
        lol = discord.Object(id)
        if not lol:
            return await ctx.send("Invalid ID provided.")
        try:
            await ctx.guild.ban(lol, reason=reason)
        except discord.Forbidden:
            await ctx.send("Oops! I don't have enough permissions to swing this ban hammer.")
        color = 0xf9e236
        em = discord.Embed(color=color, title='Banned!')
        em.add_field(name="ID", value=id)
        em.add_field(name='Banned By', value=ctx.author.name)
        reason = reason if reason is not None else 'No reason given.'
        em.add_field(name='Reason', value=reason)
        await ctx.send(embed=em)
        


        
    # @commands.group(invoke_without_command = True)
    # @commands.has_permissions(administrator = True)
    # async def banword(self, ctx, word=None):
    #     '''Command group that allows you to add/delete banned words for your server.'''
    #     em = discord.Embed(color=0xf9e236, title='Banned Words')
    #     em.description = ''
    #     try:
    #         f = open("data/guildconfig.json").read()
    #         x = json.loads(f)
    #         for i in x[str(ctx.guild.id)]["censoredWords"]:
    #             em.description += f"{i[word]} \n"
    #         await ctx.send(embed=em)
    #     except:
    #         em.description = "You have not added any ban words for this guild."
    #         return await ctx.send(embed=em)




    # @banword.command()
    # async def add(self, ctx, *, word=None):
    #     '''Adds a word to the ban list'''
    #     if word is None:
    #         await ctx.send("Please enter a word to add it to the censor.")
    #     else:
    #         f = open("data/guildconfig.json").read()
    #         x = json.loads(f)
    #         x[ctx.guild.id] = {
    #             "censoredWords":[word]
    #         }
    #         y = open("data/guildconfig.json","w")
    #         y.write(json.dumps(x, indent=4))
    #         try:
    #             await ctx.message.delete()
    #         except discord.Forbidden:
    #             pass
    #         await ctx.send("Success. The word has been added to the censor. :white_check_mark:")


    # @banword.command()
    # async def remove(self, ctx, *, word=None):
    #     '''Removes a word from the ban list.'''
    #     if word is None:
    #         await ctx.send("Please enter a word to remove it from the censor.")
    #     else:
    #         f = open("data/guildconfig.json").read()
    #         x = json.loads(f)
    #         try:
    #             e = open("data/guildconfig.json", "w")
    #             j = json.loads(e)
    #             wordlist = j[str(ctx.guild.id)]['censoredWords']
    #             wordlist.remove(word)
    #             await ctx.send("Done. Removed the word from the ban list.")
    #         except KeyError:
    #             await ctx.send("The word was not found in the ban list.")
        

    # @commands.group()
    # async def welcomemsg(self, ctx):
    #     '''Enables/disables welcome messages for this guild.'''
    #     em = discord.Embed(color=0x00ff00, title='Welcome Messages')
    #     try:
    #         f = open(f"data/welcome/{ctx.guild.id}.json").read()
    #         x = json.loads(f)
    #         em.description = f"Your current welcome message is set to: \n{x['message']['msg']}"
    #     except:
    #         em.description = "No welcome message found for the guild. \n\n**How to Use:**\n`*welcome on`: Turns on welcome messages.\n`*welcome off`: Turns off welcome messages."
    #         return await ctx.send(embed=em)
        

    # @welcomemsg.command()
    # async def on(self, ctx):
    #     await ctx.send("Enabling welcome messages. Ready for takeoff!", delete_after=3)
    #     await asyncio.sleep(3)
    #     await ctx.send("Which channel would you like the messages to be sent in? Mention the channel.")
    #     try:
    #         x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)        
    #         if not x.content.startswith("<#") and not x.content.endswith(">"):
    #             return await ctx.send("Invalid channel provided. Please mention a valid channel.")
    #     except asyncio.TimeoutError:
    #         return await ctx.send("The request timed out. Please try again.")
    #     await ctx.send(f"The channel {x.content} has been set.")
    #     await ctx.send("Please enter the message you want to display. \n\n```Variables: \n{name}: The name of the member.\n{mention}: Tag the memebr.\n{membercount}: The number of members in the guild. \n{guild}: The guild's name.```")
    #     try:
    #         f = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=90.0)
    #     except asyncio.TimeoutError:
    #         return await ctx.send("The request timed out. Please try again.")
    #     await ctx.send("Your message has been set.")
    #     await asyncio.sleep(1)
    #     msg = await ctx.send("Please wait while we load your data...")
    #     a = open(f"data/welcome/{ctx.guild.id}.json", "w")
    #     data = {
    #         "msg": f.content,
    #         "channel": x.content.strip("<").strip("#").strip(">")
    #     }
    #     b = json.load(a)
    #     b.write(json.dumps(ctx.guild.id, data, indent=4)
    #     await ctx.send("Successfully set welcome messages! :yum:   ")




def setup(bot): 
    bot.add_cog(mod(bot))        
