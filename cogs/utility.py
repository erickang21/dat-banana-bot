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
from pygoogling.googling import GoogleSearch
from .utils.paginator import Pages
from discord.ext import commands


class Utility:
    def __init__(self, bot):
       self.bot = bot

    @commands.command()
    async def searchemoji(self, ctx, *, emoji):
        """Searches an emoji from the bot's servers."""
        await ctx.message.delete()
        e = discord.utils.get(self.bot.emojis, name=emoji)
        if e is None:
            return await ctx.send("No emoji found from the list of my servers.\nThe bot cannot search YOUR servers, only the servers that it is currently in.")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://cdn.discordapp.com/emojis/{e.id}") as resp:
                resp = await resp.read()
                if e.animated:
                    extension = '.gif'
                else:
                    extension = '.png'
                await ctx.send(file=discord.File(resp, f"{e.name}{extension}"))

    @commands.command(aliases=['copyemoji', 'emojiadd', 'eadd'])
    @commands.has_permissions(manage_emojis = True)
    async def addemoji(self, ctx, *, emoji):
        """Adds an emoji by the emoji's name."""
        e = discord.utils.get(self.bot.emojis, name=emoji)
        if e is None:
            await ctx.send("No emoji found from the list of my servers.\nYou can reply with an emoji ID, and the bot will add it for you. Otherwise, reply 'cancel' to end the search.")
            try:
                x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=45.0)
            except asyncio.TimeoutError:
                return await ctx.send("The request timed out. Please try again.")
            if x.content.lower() == 'cancel':
                return await ctx.send("The process has ended.")
            if self.bot.get_emoji(int(x.content)) is None:
                return await ctx.send("Sorry, no emoji with that ID is found. ¯\_(ツ)_/¯")
            e = self.bot.get_emoji(int(x.content)) 
        count = 0
        animate = 0
        for x in ctx.guild.emojis:
            if not e.animated:
                if not x.animated:
                    count += 1
                else:
                    animate += 1
        if count >= 50 or animate >= 50:
            return await ctx.send(f"This server has reached the limit for custom emojis! {self.bot.get_emoji(430853757350445077)}")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://cdn.discordapp.com/emojis/{e.id}") as resp:
                img = await resp.read()
                try:
                    em = discord.Embed(color=discord.Color(value=0x00ff00), title=f"The emoji has been created in the server! Name: {e.name}")
                    await ctx.guild.create_custom_emoji(name=e.name, image=img)
                    em.set_image(url=f"https://cdn.discordapp.com/emojis/{e.id}")
                    await ctx.send(embed=em)
                except discord.Forbidden:
                    return await ctx.send("The bot does not have Manage Emojis permission.")


    @commands.command(aliases=['g', 'gg'])
    async def google(self, ctx, *, query: str = None):
        if query is None:
            return await ctx.send("Please enter a search query.")
        search = GoogleSearch(query)
        search.start_search()
        result = search.search_result
        em = discord.Embed(color=discord.Color(value=0x00ff00), title=f'Google Search Results for: {query}')
        if result == []:
            em.description = "No results for this search term was found. :x:"
            return await ctx.send(embed=em)
        else:
            em.description = f"**Top Result:**\n{result[0]}\n\n**Other Results:**\n{result[1]}\n{result[2]}\n{result[3]}\n{result[4]}\n{result[5]}"
        em.set_author(name=f"Searched by: {ctx.author.name}", icon_url=ctx.author.avatar_url)
        lol = []
        for x in result:
            lol.append(f"{x}\n")
        page = Pages(ctx, entries=lol, per_page=5)
        await page.paginate()

    
       

    @commands.command()
    async def feedback(self, ctx, *, feedback=None):
        """How do YOU want this bot to be? Give your word here."""
        if feedback is None:
            color = discord.Color(value=0xf44e42)
            em = discord.Embed(color=color, title='Error :x:')
            em.description = 'Please enter your feedback.'
            await ctx.send(embed=em)
        else:
            try:
                lol = self.bot.get_channel(413814935391567882)
                color = discord.Color(value=0x00ff00)
                em = discord.Embed(color=color, title='Feedback')
                em.description = feedback
                em.set_author(name=f"Sent by: {ctx.author.name}", icon_url=ctx.author.avatar_url)
                em.set_footer(text=f"Sent from {ctx.guild.name} in #{ctx.channel.name}", icon_url=ctx.guild.icon_url)
                await lol.send(embed=em)
                em.description = 'Thanks for sending feedback to make this bot better! :ok_hand:'
                await ctx.send(embed=em)
            except Exception as e:
                color = discord.Color(value=0xf44e42)
                em = discord.Embed(color=color, title='Error :x:')
                em.description = f"More details: \n\n{e}"
                await ctx.send(embed=em)


    @commands.command()
    async def hastebin(self, ctx, *, text=None):
        if text is None:
            await ctx.send("Please enter the text you want to put into Hastebin: *hastebin [text]")
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post("https://hastebin.com/documents", data=text) as resp:
                        resp = await resp.json()
                        color = discord.Color(value=0x00ff00)
                        em = discord.Embed(color=color, title='Hastebin-ified!')
                        em.description = f"Your Hastebin link: \nhttps://hastebin.com/{resp['key']}"
                        em.set_footer(text=f"Created by: {ctx.author.name}", icon_url=ctx.author.avatar_url)
                        await ctx.send(embed=em)
            except Exception as e:
                color = discord.Color(value=0xf44e42)
                em = discord.Embed(color=color, title='An error occured. :x:')
                em.description = f"More details: \n```{e}```"
                await ctx.send(embed=em)


    @commands.command()
    async def shortenurl(self, ctx, *, url=None):
        '''Shortens a URL through Tinyurl.'''
        if url is None:
            await ctx.send("Umm...Please enter a URL to shorten!")
        else:
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title='TinyURL Link Shortener')
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://tinyurl.com/api-create.php?url={url}') as resp:
                    resp = await resp.text()
                    em.description = f"Shortened Link: \n{resp}"
                    em.add_field(name='Original Link', value=url)
                    await ctx.send(embed=em)


    @commands.command()
    async def urban(self, ctx, *, word=None):
        '''Gets the definition of a word from Urban Dictionary.'''
        if word is None:
            await ctx.send("To use Urban Dictionary, please enter a word in this format: `*urban [word]`")
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://api.urbandictionary.com/v0/define?term={word}') as resp:
                    r = await resp.json()
                    color = discord.Color(value=0x00ff00)
                    em = discord.Embed(color=color, title=f'Urban Dictionary: {word}')
                    lol = []
                    for x in r['list']:
                        lol.append(f"{x['definition']} \n\n*{x['example']}* \n\n**Votes**\n:thumbsup: {x['thumbs_up']}  :thumbsdown: {x['thumbs_down']} \n\nDefinition written by {x['author']}")
                    ud = Pages(ctx, entries=lol, per_page=1)
                    await ud.paginate()


    @commands.command()
    async def playing(self, ctx, *, game=None):
        '''Enter a game, and it will find users in the server that are playing it.'''
        if game is None:
            await ctx.send("Please enter a game to search! Usage: *playing [game]")
        else:
            msg = ""
            members = [x for x in ctx.guild.members if str(x.activity) == game]
            for x in members:
                msg += f"{str(x)} \n"
            if msg == "":
                msg = 'No one in the server is currently playing this game!'
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title=f"Users Playing: {game}")
            em.description = msg
            await ctx.send(embed=em) 
            



    @commands.command()
    async def timer(self, ctx, timer=None):
        """Counts down till it's over! Usage: *timer [time in secs]"""
        if timer is None:
            return await ctx.send("Please enter a time in seconds! Usage: *timer [time in secs]")
        try:
            float(timer)
        except ValueError:
            await ctx.send("UH OH! Timer did not start. Usage: *timer [time in secs]. Make sure the time is a *whole number*.")
        else:
            await ctx.send("Timer started and rolling! :timer:")
            await asyncio.sleep(float(timer))
            await ctx.send("TIME'S UP! :clock:")
        
        
    @commands.command()
    async def ranint(self, ctx, a: int = None, b: int = None):
        """Usage: *ranint [least number][greatest number]. RanDOM!"""
        if a is None:
            await ctx.send("Boi, are you random! Usage: *ranint [least #] [greatest #], to set the range of the randomized number. Please use integers.")
        if b is None:
            await ctx.send("Boi, are you random! Usage: *ranint [least #] [greatest #], to set the range of the randomized number. Please use integers.")
        else:
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title='Your randomized number:')
            em.description = random.randint(a,b)
            await ctx.send(embed=em)
            
                    
    @commands.command()
    async def rolldice(self, ctx):
        """Rolls a 6 sided die."""
        choices = ['1', '2', '3', '4', '5', '6']
        color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color, title='Rolled! (1 6-sided die)', description=random.choice(choices))
        await ctx.send(embed=em)
        

    @commands.command()
    async def flipcoin(self, ctx):
        """Flip a coin. Any coin."""
        choices = ['Heads', 'Tails', 'Coin self-destructed.']
        color = discord.Color(value=0x00ff00)
        em=discord.Embed(color=color, title='Flipped a coin!')
        em.description = random.choice(choices)
        await ctx.send(embed=em)


    @commands.command()
    async def choose(self, ctx, *, args=None):
        """Can't choose. Let this bot do it for you. Seperate choices with a comma."""
        if args is None:
            await ctx.send("Oops! Usage: *choose choice, anotha choice, 3rd choice, etc")
        else:
            lol = self.bot.get_emoji(410122907373535233)
            msg = await ctx.send(lol)
            args = args.split(",")
            await asyncio.sleep(3)
            await msg.edit(content=f"I choose:\n**{random.choice(args)}**")

        
    @commands.command(aliases=['tf'])
    async def textface(self, ctx, Type=None):
        """Get those dank/cool faces here. Type *textface list for a list."""
        if Type is None:
            await ctx.send('That is NOT one of the dank textfaces in here yet. Use: *textface list to get a list of textfaces you can use.')
        else:
            if Type.lower() == 'lenny':
              await ctx.send('( ͡° ͜ʖ ͡°)')
            elif Type.lower() == 'tableflip':
              await ctx.send('(ノಠ益ಠ)ノ彡┻━┻')
            elif Type.lower() == 'shrug':
              await ctx.send('¯\_(ツ)_/¯')
            elif Type.lower() == 'bignose':
              await ctx.send('(͡ ͡° ͜ つ ͡͡°)')
            elif Type.lower() == 'iwant':
              await ctx.send('ლ(´ڡ`ლ)')
            elif Type.lower() == 'musicdude':
              await ctx.send('ヾ⌐*_*ノ♪')
            elif Type.lower() == 'wot':
              await ctx.send('ლ,ᔑ•ﺪ͟͠•ᔐ.ლ')
            elif Type.lower() == 'bomb':
              await ctx.send('(´・ω・)っ由')
            elif Type.lower() == 'orlly':
              await ctx.send("﴾͡๏̯͡๏﴿ O'RLY?")
            elif Type.lower() == 'money':
              await ctx.send('[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]')
            elif Type.lower() == 'list':
              color = discord.Color(value=0x00ff00)
              em = discord.Embed(color=color, title='List of Textfaces')
              em.description = 'Choose from the following: lenny, tableflip, shrug, bignose, iwant, musicdude, wot, bomb, orlly, money. Type *textface [face].'
              em.set_footer(text="Don't you dare question my names for the textfaces.")
              await ctx.send(embed=em)
            else:
              await ctx.send('That is NOT one of the dank textfaces in here yet. Use *textface list to see a list of the textfaces.')
            
            
    @commands.command(aliases=['av'])
    async def avatar(self, ctx, user: discord.Member = None):
        """Returns a user's avatar url. Use *av [user], or just *av for your own."""
        if user is None:
            av = ctx.message.author.avatar_url
            if '.gif' in av:
                av += "&f=.gif"
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title=ctx.message.author.name)
            em.set_author(name='Profile Picture')
            em.set_image(url=av)
            await ctx.send(embed=em)                  
        else:
            av = user.avatar_url
            if '.gif' in av:
                av += "&f=.gif"
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title=user.name)
            em.set_author(name='Profile Picture')
            em.set_image(url=av)
            await ctx.send(embed=em)
            
            
    @commands.command()
    async def userinfo(self, ctx, user: discord.Member = None):
        """Dig out that user info. Usage: *userinfo [tag user]"""
        if user is None:
            color = discord.Color(value=0xf2f760)
            em = discord.Embed(color=color, title=f'User Info: {ctx.message.author.name}')
            em.add_field(name='Status', value=f'{ctx.message.author.status}')       
            em.add_field(name='Account Created', value=ctx.message.author.created_at.__format__('%A, %B %d, %Y'))
            em.add_field(name='ID', value=f'{ctx.message.author.id}')
            if ctx.message.author.bot:
                Type = 'Bot'
            else:
                Type = 'Human'
            em.add_field(name='Profile Type', value=Type)
            em.set_thumbnail(url=ctx.message.author.avatar_url)
            await ctx.send(embed=em)
        else:
            color = discord.Color(value=0xf2f760)
            em = discord.Embed(color=color, title=f'User Info: {user.name}')
            em.add_field(name='Status', value=f'{user.status}')       
            em.add_field(name='Account Created', value=user.created_at.__format__('%A, %B %d, %Y'))
            em.add_field(name='ID', value=f'{user.id}')
            if user.bot:
                Type = 'Bot'
            else:
                Type = 'Human'
            em.add_field(name='Profile Type', value=Type)
            em.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=em)    
        
              
    @commands.command()
    async def serverinfo(self, ctx):
        """Are you a nerd? Here's some server info."""
        guild = ctx.guild
        roles = [x.name for x in guild.roles]
        role_length = len(roles)
        roles = ', '.join(roles)
        channels = len(guild.channels)
        time = str(guild.created_at.strftime("%b %m, %Y, %A, %I:%M %p"))         
        em = discord.Embed(description= "-", title='Server Info', colour=0x00ff00)
        em.set_thumbnail(url=guild.icon_url)
        em.add_field(name='__Server __', value=str(guild.name))
        em.add_field(name='__Server ID__', value=str(guild.id))
        em.add_field(name='__Owner__', value=str(guild.owner))
        em.add_field(name='__Owner ID__', value=guild.owner_id) 
        em.add_field(name='__Member Count__', value=str(guild.member_count))
        em.add_field(name='__Text/Voice Channels__', value=str(channels))
        em.add_field(name='__Server Region__', value='%s' % str(guild.region))
        em.add_field(name='__ Total Roles__', value='%s' % str(role_length))
        em.add_field(name='__Roles__', value='%s' % str(roles))
        em.set_footer(text='Created - %s' % time)        
        await ctx.send(embed=em)
              

    @commands.command()
    async def roleinfo(self, ctx, *, rolename=None):
        try:
            role = discord.utils.get(ctx.guild.roles, name=rolename)
        except:
            return await ctx.send("Role not found. Please make sure the role name is correct. (Case Sensitive!)")
        em = discord.Embed(color=role.color, title=f'Role Info: {rolename}')
        p = ""
        if role.permissions.administrator:
            p += "Administrator :white_check_mark: \n"
        else:
            p += "Administrator :x: \n"
        if role.permissions.create_instant_invite:
            p += "Create Instant Invite :white_check_mark: \n"
        else:
            p += "Create Instant Invite :x:\n"
        if role.permissions.kick_members:
            p += "Kick Members :white_check_mark: \n"
        else:
            p += "Kick Members :x:\n"
        if role.permissions.ban_members:
            p += "Ban Members :white_check_mark: \n"
        else:
            p += "Ban Members :x:\n"
        if role.permissions.manage_channels:
            p += "Manage Channels :white_check_mark: \n"
        else:
            p += "Manage Channels :x:\n"
        if role.permissions.manage_guild:
            p += "Manage Server :white_check_mark: \n"
        else:
            p += "Manage Server :x:\n"
        if role.permissions.add_reactions:
            p += "Add Reactions :white_check_mark: \n"
        else:
            p += "Add Reactions :x:\n"
        if role.permissions.view_audit_log:
            p += "View Audit Log :white_check_mark: \n"
        else:
            p += "View Audit Log :x:\n"
        if role.permissions.read_messages:
            p += "Read Messages :white_check_mark: \n"
        else:
            p += "Read Messages :x:\n"
        if role.permissions.send_messages:
            p += "Send Messages :white_check_mark: \n"
        else:
            p += "Send Messages :x:\n"
        if role.permissions.send_tts_messages:
            p += "Send TTS Messages :white_check_mark: \n"
        else:
            p += "Send TTS Messages :x:\n"
        if role.permissions.manage_messages:
            p += "Manage Messages :white_check_mark: \n"
        else:
            p += "Manage Messages :x:\n"
        if role.permissions.embed_links:
            p += "Embed Links :white_check_mark: \n"
        else:
            p += "Embed Links :x:\n"
        if role.permissions.attach_files:
            p += "Attach Files :white_check_mark: \n"
        else:
            p += "Attach Files \n" 
        if role.permissions.read_message_history:
            p += "Read Message History :white_check_mark: \n"
        else:
            p += "Read Message History :x:\n"
        if role.permissions.mention_everyone:
            p += "Mention @everyone :white_check_mark: \n"
        else:
            p += "Mention @everyone :x:\n"
        if role.permissions.external_emojis:
            p += "Use External Emojis :white_check_mark: \n"
        else:
            p += "Use External Emojis :x:\n"
        if role.permissions.change_nickname:
            p += "Change Nicknames :white_check_mark: \n"
        else:
            p += "Change Nicknames :x:\n"
        if role.permissions.manage_nicknames:
            p += "Manage Nicknames :white_check_mark: \n"
        else:
            p += "Manage Nicknames :x:\n"
        if role.permissions.manage_roles:
            p += "Manage Roles :white_check_mark: \n"
        else:
            p += "Manage Roles :x:\n"
        if role.permissions.manage_webhooks:
            p += "Manage Webhooks :white_check_mark: \n"
        else:
            p += "Manage Webhooks :x:\n"
        if role.permissions.manage_emojis:
            p += "Manage Emojis :white_check_mark: \n"
        else:
            p += "Manage Emojis :x:\n"
        v = "" 
        if role.permissions.connect:
            v += "Connect :white_check_mark: \n"
        else:
            v += "Connect :x:\n"
        if role.permissions.speak:
            v += "Speak :white_check_mark: \n"
        else:
            v += "Speak :x:\n"
        if role.permissions.mute_members:
            v += "Mute Members :white_check_mark: \n"
        else:
            v += "Mute Members :x:\n"
        if role.permissions.deafen_members:
            v += "Deafen Members :white_check_mark: \n"
        else:
            v += "Deafen Members :x:\n"
        if role.permissions.move_members:
            v += "Move Members :white_check_mark: \n"
        else:
            v += "Move Members :x:\n"
        if role.permissions.use_voice_activation:
            v += "Use Voice Activation :white_check_mark: \n"
        else:
            v += "Use Voice Activation :x:\n"
        em.description = f"**General Permissions** \n\n{p} \n\n\n**Voice Permissions** \n\n{v}"
        em.add_field(name='ID', value=role.id)
        em.add_field(name='Position from Bottom', value=role.position)
        if role.mentionable:
            a = 'Mentionable'
        else:
            a = 'Not Mentionable'
        em.add_field(name='Mentionable', value=a)
        em.add_field(name='Time Created', value=str(role.created_at.strftime("%A, %b %m, %Y at %I:%M %p")))
        member = ""
        for x in role.members:
            member += f"{x.name} \n"
        em.add_field(name='Members in the Role', value=member)
        await ctx.send(embed=em)





def setup(bot): 
    bot.add_cog(Utility(bot))               
