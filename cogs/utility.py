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
from .utils.paginator import Pages
from discord.ext import commands


class Utility:
    def __init__(self, bot):
       self.bot = bot
       

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
            members = ctx.guild.members
            for x in members:
                if x.game != None:
                    if x.game.name == game:
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
            p += "    Administrator :white_check_mark: \n"
        else:
            p += ":x: Administrator \n"
        if role.permissions.create_instant_invite:
            p += "    Create Instant Invite :white_check_mark: \n"
        else:
            p += ":x: Create Instant Invite"
        if role.permissions.kick_members:
            p += "    Kick Members :white_check_mark: \n"
        else:
            p += ":x: Kick Members \n"
        if role.permissions.ban_members:
            p += "    Ban Members :white_check_mark: \n"
        else:
            p += ":x: Ban Members \n"
        if role.permissions.manage_channels:
            p += "    Manage Channels :white_check_mark: \n"
        else:
            p += ":x: Manage Channels \n"
        if role.permissions.manage_guild:
            p += "    Manage Server :white_check_mark: \n"
        else:
            p += ":x: Manage Server \n"
        if role.permissions.add_reactions:
            p += "    Add Reactions :white_check_mark: \n"
        else:
            p += ":x: Add Reactions \n"
        if role.permissions.view_audit_log:
            p += "    View Audit Log :white_check_mark: \n"
        else:
            p += ":x: View Audit Log \n"
        if role.permissions.read_messages:
            p += "    Read Messages :white_check_mark: \n"
        else:
            p += ":x: Read Messages \n"
        if role.permissions.send_messages:
            p += "    Send Messages :white_check_mark: \n"
        else:
            p += ":x: Send Messages \n"
        if role.permissions.send_tts_messages:
            p += "    Send TTS Messages :white_check_mark: \n"
        else:
            p += ":x: Send TTS Messages \n"
        if role.permissions.manage_messages:
            p += "    Manage Messages :white_check_mark: \n"
        else:
            p += ":x: Manage Messages \n"
        if role.permissions.embed_links:
            p += "    Embed Links :white_check_mark: \n"
        else:
            p += ":x: Embed Links \n"
        if role.permissions.attach_files:
            p += "    Attach Files :white_check_mark: \n"
        else:
            p += ":x: Attach Files \n" 
        if role.permissions.read_message_history:
            p += "    Read Message History :white_check_mark: \n"
        else:
            p += ":x: Read Message History \n"
        if role.permissions.mention_everyone:
            p += "    Mention @everyone :white_check_mark: \n"
        else:
            p += ":x: Mention @everyone \n"
        if role.permissions.external_emojis:
            p += "    Use External Emojis :white_check_mark: \n"
        else:
            p += ":x: Use External Emojis \n"
        if role.permissions.change_nickname:
            p += "    Change Nicknames :white_check_mark: \n"
        else:
            p += ":x: Change Nicknames \n"
        if role.permissions.manage_nicknames:
            p += "    Manage Nicknames :white_check_mark: \n"
        else:
            p += ":x: Manage Nicknames \n"
        if role.permissions.manage_roles:
            p += "    Manage Roles :white_check_mark: \n"
        else:
            p += ":x: Manage Roles \n"
        if role.permissions.manage_webhooks:
            p += "    Manage Webhooks :white_check_mark: \n"
        else:
            p += ":x: Manage Webhooks \n"
        if role.permissions.manage_emojis:
            p += "    Manage Emojis :white_check_mark: \n"
        else:
            p += ":x: Manage Emojis \n"
        v = "" 
        if role.permissions.connect:
            v += "    Connect :white_check_mark: \n"
        else:
            v += ":x: Connect \n"
        if role.permissions.speak:
            v += "    Speak :white_check_mark: \n"
        else:
            v += ":x: Speak \n"
        if role.permissions.mute_members:
            v += "    Mute Members :white_check_mark: \n"
        else:
            v += ":x: Mute Members \n"
        if role.permissions.deafen_members:
            v += "    Deafen Members :white_check_mark: \n"
        else:
            v += ":x: Deafen Members \n"
        if role.permissions.move_members:
            v += "    Move Members :white_check_mark: \n"
        else:
            v += ":x: Move Members \n"
        if role.permissions.use_voice_activation:
            v += "    Use Voice Activation :white_check_mark: \n"
        else:
            v += ":x: Use Voice Activation \n"
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
            member += f"{x} \n"
        em.add_field(name='Members in the Role', value=x)
        await ctx.send(embed=em)





def setup(bot): 
    bot.add_cog(Utility(bot))               