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
            await ctx.channel.set_permissions(discord.utils.get(ctx.guild.roles, id=ctx.guild.id), send_messages=False)
            return await msg.edit(content="The channel has been successfully locked down. :lock: ")
        elif action.lower() == 'off':
            msg = await ctx.send("Unlocking the channel...")        
            await ctx.channel.set_permissions(discord.utils.get(ctx.guild.roles, id=ctx.guild.id), send_messages=True)
            return await msg.edit(content="The channel has been successfully unlocked. :unlock: ")
        else:
            return await ctx.send("Lockdown command:\n*lockdown [on/off]")



    

        
    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def dm(self, ctx, user: discord.Member, *, msg: str):
        """Escort your DM to someone thru the bot. Usage: *dm [tag person] [msg]"""
        #if not self.dev_check(ctx.author.id):
        #    return await ctx.send("You cannot use this command because you are not a developer.")
        try:
            em = discord.Embed(color=ctx.author.color, title="New Message")
            em.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
            em.description = msg
            em.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
            await user.send(embed=em)
            await ctx.message.delete()            
            await ctx.send("SuccESS! Your DM has made it! :white_check_mark: ")
        except commands.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with DM'ing people without permissions.")
        except:
            await ctx.send("Error :x:. Make sure your message is shaped in this way: *dm [tag person] [msg]")


    
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def warn(self, ctx, user: discord.Member, *, reason: str):
        """It's time to stop. Sends that warning. Usage: *warn [tag person] [reason]"""
        try:
            color = 0xf44242
            em = discord.Embed(color=color, title=f"You have been warned.")
            em.description = textwrap.dedent(f"""
            {self.bot.get_emoji(430340802879946773)} **Warned By**
            {str(ctx.author)}

            :house: **Server**
            {ctx.guild.name}

            :speech_balloon: **Reason**
            {reason}
            """)
            await user.send(embed=em)
            await ctx.message.delete()
            await ctx.send("User has been DM'd :white_check_mark:. Pray that the user is a gud boi now. :pray:", delete_after=3)
            modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
            if modlog:
                em = discord.Embed(color=discord.Color(value=0x00ff00), title="Member Warned")
                em.description = textwrap.dedent(f"""
                {self.bot.get_emoji(430340802879946773)} **Warned By**
                {str(ctx.author)}

                :house: **Server**
                {ctx.guild.name}

                :speech_balloon: **Reason**
                {reason}
                """)
            
                channel = self.bot.get_channel(int(modlog['channel']))
                if channel:
                    await channel.send(embed=em)
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
        if ctx.author.roles[-1].position < user.roles[-1].position:
            return await ctx.send(f"Sorry, but **{str(user)}**'s top role is higher than yours. No can do!")
        elif ctx.author.roles[-1].position == user.roles[-1].position:
            return await ctx.send(f"Sorry, but **{str(user)}**'s top role is equal to yours. No can do!")
        if not ctx.guild.me.guild_permissions.kick_members:
            return await ctx.send("Oops! I don't have enough permissions to use the boot.")
        try:
            await user.send(f"{self.bot.get_emoji(505723800068030464)} You have been kicked from **{ctx.guild.name}**.\n\n**Reason:** {reason}")
        except:
            pass
        try:
            await user.kick(reason=f"{str(ctx.author)}: {reason}")
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
            em.set_image(url="https://cdn.weeb.sh/images/H16aQJFvb.gif")
            await ctx.send(embed=em)
            modlog = await self.bot.db.modlog.find_one({"id": str(ctx.guild.id)})
            if modlog:
                em = discord.Embed(color=discord.Color(value=0x00ff00), title="Member Kicked")
                em.description = textwrap.dedent(f"""
                :zipper_mouth: User: {str(user)}

                {self.bot.get_emoji(430340802879946773)} Kicked by: {str(ctx.author)}

                :1234: User ID: {user.id}
                """)
            
                channel = self.bot.get_channel(int(modlog['channel']))
                if channel:
                    await channel.send(embed=em)
        except discord.Forbidden:
            await ctx.send("Oops! I don't have enough permissions to use the boot.")
        
        
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        """Swings the mighty Ban Hammer on that bad boy."""
        if user.id == ctx.author.id:
            return await ctx.send("I don't understand your logic. Using the ban hammer on yourself?")
        if ctx.author.roles[-1].position < user.roles[-1].position:
            return await ctx.send(f"Sorry, but **{str(user)}**'s top role is higher than yours. No can do!")
        elif ctx.author.roles[-1].position == user.roles[-1].position:
            return await ctx.send(f"Sorry, but **{str(user)}**'s top role is equal to yours. No can do!")
        if not ctx.guild.me.guild_permissions.ban_members:
            return await ctx.send("Oops! I don't have enough permissions to swing this ban hammer.")
        try:
            await user.send(f"{self.bot.get_emoji(505723800068030464)} You have been banned from **{ctx.guild.name}**.\n\n**Reason:** {reason}")
        except:
            pass
        try:
            await user.ban(reason=reason, delete_message_days=0)
        except discord.Forbidden:
            return await ctx.send("Oops! I don't have enough permissions to swing this ban hammer.")
        color = 0xf9e236
        em = discord.Embed(color=color, title='Banned!')
        em.description = f'The ban hammer has fell down.'
        em.set_image(url="https://i.kym-cdn.com/photos/images/newsfeed/001/118/143/5ec.gif")
        em.add_field(name='User', value=user.name)
        em.add_field(name='Banned By', value=ctx.author.name)
        reason = reason if reason is not None else 'No reason given.'
        em.add_field(name='Reason', value=f"{str(ctx.author)}: {reason}")
        em.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=em)
        



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
        try:
            await ctx.channel.set_permissions(user, send_messages=True)
            await ctx.channel.send(f"{user.mention} is now un-shutted up.")
        except discord.Forbidden:
            await ctx.send("Couldn't unmute the user. Uh-oh...")
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

       
    

    @commands.command(aliases=['arole'])
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
    async def addrole(self, ctx, user: discord.Member, *, role):
        """Adds a role to a user."""
        r = discord.utils.get(ctx.guild.roles, name=str(role))
        if r is None:   
            return await ctx.send("Role not found. Please note that roles are case sensitive!")
        if ctx.author.roles[-1].position < r.position:
            return await ctx.send(f"Sorry, but the position of **{str(r)}** is higher than yours. No can do!")
        elif ctx.author.roles[-1].position == r.position:
            return await ctx.send(f"Sorry, but the position of **{str(r)}** is equal to yours. No can do!")
        role = await Utils.clean_text(ctx, role)
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
        if ctx.author.roles[-1].position < r.position:
            return await ctx.send(f"Sorry, but the position of **{str(r)}** is higher than yours. No can do!")
        elif ctx.author.roles[-1].position == r.position:
            return await ctx.send(f"Sorry, but the position of **{str(r)}** is equal to yours. No can do!")
        role = await Utils.clean_text(ctx, role)
        if r.name not in [x.name for x in user.roles]:
            return await ctx.send(f"Looks like **{str(user)}** never had the role **{role}**.")
        try:
            await user.remove_roles(r)
            return await ctx.send(f"Success! **{str(user)}** has been removed from the role **{role}**.")
        except discord.Forbidden:
            return await ctx.send("Bot does not have enough permissions to remove role.")
        
            
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def hackban(self, ctx, id : int, *, reason=None):
        if ctx.guild.get_member(id):
            return await ctx.send("Senpai, hackban is to ban people **not in the server.** If you wanna ban someone in the server, run `*ban @user`.")
        if not ctx.guild.me.guild_permissions.kick_members:
            return await ctx.send("Oops! I don't have enough permissions to use the boot.")
        try:
            id = int(id)
        except ValueError:
            return await ctx.send("Did you enter a valid user ID?")
        lol = discord.Object(id)
        if not lol:
            return await ctx.send("Invalid ID provided.")
        try:
            await ctx.guild.ban(lol, reason=reason, delete_message_days=0)
        except discord.Forbidden:
            await ctx.send("Oops! I don't have enough permissions to swing this ban hammer.")
        data = await self.bot.get_user_info(id)
        color = 0xf9e236
        em = discord.Embed(color=color, title='Banned!')
        em.add_field(name="User", value=str(data))
        em.add_field(name="ID", value=id)
        em.add_field(name='Banned By', value=ctx.author.name)
        em.set_image(url="https://i.kym-cdn.com/photos/images/newsfeed/001/118/143/5ec.gif")
        reason = reason if reason is not None else 'No reason given.'
        em.add_field(name='Reason', value=reason)
        em.set_thumbnail(url=data.avatar_url)
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
