import discord
import sys
import os
import io
import asyncio
import json
import ezjson
from discord.ext import commands


class mod:
    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def dm(self, ctx, user: discord.Member, *, msg: str):
        """Escort your DM to someone thru the bot. Usage: *dm [tag person] [msg]"""
        try:
            await user.send(msg)
            await ctx.message.delete()            
            await ctx.send("SuccESS! Your DM has made it! :white_check_mark: ")
        except commands.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with DM'ing people without permissions.")
        except:
            await ctx.send("Error :x:. Make sure your message is shaped in this way: *dm [tag person] [msg]")


    
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def warn(self, ctx, user: discord.Member, *, reason: str):
        """It's time to stop. Sends that warning. Usage: *warn [tag person] [reason]"""
        try:
            color = discord.Color(value=0xf44242)
            em = discord.Embed(color=color, title=f"WARNING: by {ctx.message.author.name} from **{ctx.author.guild.name}**.", description=f"{reason}")
            await user.send(embed=em)
            await ctx.message.delete()
            await ctx.send("User has been DM'd :white_check_mark:. Pray that the user is a gud boi now. :pray:")
        except discord.ext.commands.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with warning people without permissions.")
        except:
            await ctx.send("Something happened and the DM could not make it :x:. The user could be blocking DMs from the server, or you did not use the format correctly. Usage: *warn [tag person] [reason].")    
       
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def purge(self, ctx, num: int):
        """Deletes a # of msgs. *purge [# of msgs].""" 
        try: 
            if num is None:
                await ctx.send("How many messages would you like me to delete? Usage: *purge [number of msgs]")
            else:
                try:
                    float(num)
                except ValueError:
                    return await ctx.send("The number is invalid. Make sure it is valid! Usage: *purge [number of msgs]")
                await ctx.channel.purge(limit=num+1)
                msg = await ctx.send("Purged successfully :white_check_mark:", delete_after=3)
        except discord.Forbidden:
            await ctx.send("Purge unsuccessful. The bot does not have Manage Msgs permission.")
        except commands.errors.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with purging without permissions.")
    
    
    @commands.command()
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, user: discord.Member = None, *, reason=None):
        """Kicks a member into the world outside your server."""
        if user is None:
            await ctx.send("To boot the member, use the command like this: \n*kick [@user] [reason]")
        try:
            await user.kick(reason=reason)
            color = discord.Color(value=0x00ff00)
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
        except commands.errors.MissingPermissions:
            await ctx.send("Nice try. You need `Kick Members` Permission to use this!")
        
        
    
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, user: discord.Member = None, msgdeletedays: int = 0, *, reason=None):
        """Swings the mighty Ban Hammer on that bad boy."""
        if user is None:
            await ctx.send("To swing the ban hammer, use the command like this: \n*ban [@user] [days of msgs to delete] [reason]")
        try:
            await user.ban(delete_message_days=msgdeletedays, reason=reason)
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title='Banned!')
            em.add_field(name='User', value=user.name)
            em.add_field(name='Banned By', value=ctx.author.name)
            em.add_field(name='Days of Messages Deleted', value=f"{msgdeletedays} days")
            if reason is None:
                reason = 'No reason given.'
            else:
                reason = reason
            em.add_field(name='Reason', value=reason)
            em.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=em)
        except discord.Forbidden:
            await ctx.send("Oops! I don't have enough permissions to swing this ban hammer.")
        except commands.errors.MissingPermissions:
            await ctx.send("Nice try. You need `Ban Members` Permissions to use this!")



    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def mute(self, ctx, user: discord.Member, mutetime=None):
        '''Forces someone to shut up. Usage: *mute [user] [time in mins]'''
        try:
            if mutetime is None:
                await ctx.channel.set_permissions(user, send_messages=False)
                await ctx.send(f"{user.mention} is now forced to shut up. :zipper_mouth: ")
            else:
                try:
                    mutetime =int(mutetime)
                    mutetime = mutetime * 60
                except ValueError:
                    return await ctx.send("Your time is an invalid number. Make sure...it is a number.")
                await ctx.channel.set_permissions(user, send_messages=False)
                await ctx.channel.send(f"{user.mention} is now forced to shut up. :zipper_mouth: ")
                await asyncio.sleep(mutetime)
                await ctx.channel.set_permissions(user, send_messages=True)
                await ctx.channel.send(f"{user.mention} is now un-shutted up.")
        except discord.Forbidden:
            return await ctx.send("I could not mute the user. Make sure I have the manage channels permission.")
        except commands.errors.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with shutting someone up without permissions.")


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def servermute(self, ctx, user: discord.Member = None):
        '''Forces someone to shut up through the entire server. OUCH.'''
        if user is None:
            await ctx.send("Bruh. Tag a user to mute them...")
        else:
            msg = await ctx.send("Muting user...")
            try:
                lol = discord.utils.get(ctx.guild.roles, name='Muted')
                await user.add_roles(lol)
            except:
                try:
                    role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(permissions=68420672)) 
                    # Given permissions: Change nickname, read messages, use external emojis, add reactions, 
                    # voice: view channel, voice: connect. EVERYTHING ELSE IS DISABLED.
                    await user.add_roles(role)
                except discord.Forbidden:
                    return await msg.edit(content="Don't have enough permissions. For flawless bot functions, give the Administrator permission to the bot.")
            await msg.edit(content="The user has been muted for this server. :zipper_mouth:")


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def serverunmute(self, ctx, user: discord.Member = None):
        '''Un-shuts someone up from the entire server. YEEE.'''
        if user is None:
            await ctx.send("Bruh. Tag a user to unmute them...")
        else:
            msg = await ctx.send("Unmuting user...")
            try:
                await user.remove_roles("Muted")
            except discord.Forbidden:
                return await ctx.send("Uh-oh! Not enough permissions!")
            await msg.edit(content="The user has been unmuted for this server. :grin:")



    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unmute(self, ctx, user: discord.Member):
        '''Allows someone to un-shut up. Usage: *unmute [user]'''
        try:
            await ctx.channel.set_permissions(user, send_messages=True)
            await ctx.channel.send(f"{user.mention} is now un-shutted up.")
        except discord.Forbidden:
            await ctx.send("Couldn't unmute the user. Uh-oh...")
        except commands.errors.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with shutting someone up without permissions.")              
        
        
    @commands.group(invoke_without_command = True)
    @commands.has_permissions(administrator = True)
    async def banword(self, ctx, word=None):
        '''Command group that allows you to add/delete banned words for your server.'''
        em = discord.Embed(color=discord.Color(value=0x00ff00), title='Banned Words')
        em.description = ''
        try:
            f = open("data/guildconfig.json").read()
            x = json.loads(f)
            for i in x[str(ctx.guild.id)]["censoredWords"]:
                em.description += f"{i[word]} \n"
            await ctx.send(embed=em)
        except:
            em.description = "You have not added any ban words for this guild."
            return await ctx.send(embed=em)




    @banword.command()
    async def add(self, ctx, *, word=None):
        '''Adds a word to the ban list'''
        if word is None:
            await ctx.send("Please enter a word to add it to the censor.")
        else:
            f = open("data/guildconfig.json").read()
            x = json.loads(f)
            x[ctx.guild.id] = {
                "censoredWords":[word]
            }
            y = open("data/guildconfig.json","w")
            y.write(json.dumps(x, indent=4))
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
            await ctx.send("Success. The word has been added to the censor. :white_check_mark:")


    @banword.command()
    async def remove(self, ctx, *, word=None):
        '''Removes a word from the ban list.'''
        if word is None:
            await ctx.send("Please enter a word to remove it from the censor.")
        else:
            f = open("data/guildconfig.json").read()
            x = json.loads(f)
            try:
                e = open("data/guildconfig.json", "w")
                j = json.loads(e)
                wordlist = j[str(ctx.guild.id)]['censoredWords']
                wordlist.remove(word)
                await ctx.send("Done. Removed the word from the ban list.")
            except KeyError:
                await ctx.send("The word was not found in the ban list.")
        
def setup(bot): 
    bot.add_cog(mod(bot))        