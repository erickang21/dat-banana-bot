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
from .utils.paginator import Pages
from discord.ext import commands


class Utility:
    def __init__(self, bot):
       self.bot = bot
       

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
            await msg.edit(content=f"I choose:\n{random.choice(args)}")

        
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
            if ctx.message.author.bot is True:
                type = 'Bot'
            else:
                type = 'Human'
            em.add_field(name='Profile Type', value=type)
            em.set_thumbnail(url=ctx.message.author.avatar_url)
            await ctx.send(embed=em)
        else:
            color = discord.Color(value=0xf2f760)
            em = discord.Embed(color=color, title=f'User Info: {user.name}')
            em.add_field(name='Status', value=f'{user.status}')       
            em.add_field(name='Account Created', value=user.created_at.__format__('%A, %B %d, %Y'))
            em.add_field(name='ID', value=f'{user.id}')
            if user.bot is True:
                type = 'Bot'
            else:
                type = 'Human'
            em.add_field(name='Profile Type', value=type)
            em.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=em)    
        
              
              
def setup(bot): 
    bot.add_cog(Utility(bot))               
