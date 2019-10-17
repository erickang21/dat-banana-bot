import discord
import sys
import os
import io
import asyncio
#import psutil
import time
import re
import json
import textwrap
import subprocess
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starttime = self.bot.starttime
        
    def dev_check(self, id):
        with open('data/devs.json') as f:
            devs = json.load(f)
            if id in devs:
                return True
        return False

    @commands.command(aliases=['info', 'botinfo'])
    async def stats(self, ctx):
        """Statsies for this bot. Be a nerd!"""       
        color = 0xf9e236
        #RAM = psutil.virtual_memory()
        #used = RAM.used >> 20
        #percent = RAM.percent
        member = 0
        for i in self.bot.guilds:
            for x in i.members:
                member += 1
        second = time.time() - self.starttime
        minute, second = divmod(second, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)
        lol = subprocess.run(f"python3 -V", cwd=os.getcwd(), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        err = lol.stderr.decode("utf-8")
        res = lol.stdout.decode("utf-8")
        #content = (await self.bot.get_channel(392464990658887681).history(limit=1).flatten())[0].content
        #version = re.findall(r"v(\d.\d.\d)", content)[0]
        em = discord.Embed(color=color, title='Bot Stats')
        em.set_thumbnail(url=self.bot.user.avatar_url)        
        em.add_field(name='Creator', value=f'kawaii banana ☆#5627')
        em.add_field(name='Devs', value='PoLLeN#5796')
        em.add_field(name='Servers :homes: ', value=f'{len(self.bot.guilds)}')
        em.add_field(name='Total Members :busts_in_silhouette: ', value=member)
        #em.add_field(name='Latency :ping_pong: ', value=f"{self.bot.latency * 1000:.4f} ms")
        #em.add_field(name='Version', value=version)
        #em.add_field(name=f'Start Date :calendar:', value='12/08/2017')
        em.add_field(name='Coding Language :computer: ', value=res) 
        #em.add_field(name=f'Hosting Platform {self.bot.get_emoji(440698056346697728)}', value='Digital Ocean') 
        #em.add_field(name='Memory Usage', value=f"{used} MB ({percent}%)")
        em.add_field(name='Bot Uptime :clock:', value="%d days, %d hours, %d minutes, %d seconds" % (day, hour, minute, second)) 
        em.add_field(name='Commands Run (Since Uptime) :outbox_tray:', value=self.bot.commands_run)  
        await ctx.send(embed=em)

    @commands.command()
    async def dbstats(self, ctx):
        names = await self.bot.db.collection_names()
        db_stuff = "**Database: MongoDB**\n\n"
        for name in names:
            count = await getattr(self.bot.db, name).count() 
            db_stuff += f"**{name}:** {count} entries\n"
        em = discord.Embed(color=ctx.author.color, title="Database Stats")
        em.description = db_stuff
        em.set_footer(text=f"Requested by: {str(ctx.author)}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    # @commands.command(aliases=['updates', 'bu', 'botu'])
    # async def botupdates(self, ctx):
    #     """Read the latest notes on the latest update!"""    
    #     content = (await self.bot.get_channel(392464990658887681).history(limit=1).flatten())[0].content
    #     title = content.split("\n")[0].replace("*", "")
    #     em = discord.Embed(color=discord.Color(value=0xf9e236))
    #     em.description = content
    #     await ctx.send(embed=em)

    @commands.command()
    async def bugs(self, ctx, action=None, *, bug=None):
        if not action and not bug:
            count = await self.bot.db.bugs.count()
            bugs = """
**The following bugs are already known and are listed by developers that have tested the bot.**

If you happen to know one that is not listed below, please report it with `*bugs report [describe the bug]`.\n
"""
            for i in range(count):
                bug = await self.bot.db.bugs.find_one({"index": i})
                bugs += f"- {bug['bug']}\n"
            em = discord.Embed(color=ctx.author.color, title="Known Bugs")
            em.description = bugs
            em.set_footer(text=f"Requested by: {str(ctx.author)}", icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=em)
        elif action.lower() == "add":
            if not self.dev_check(ctx.author.id):
                return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {bot.get_emoji(555121740465045516)}")
            count = await self.bot.db.bugs.count()
            await self.bot.db.bugs.update_one({"index": count}, {"$set": {"bug": bug}}, upsert=True)
            return await ctx.send(f"Success! The bug will now be listed when the `*bugs` command is ran. {self.bot.get_emoji(522530578860605442)}")
        elif action.lower() == "report":
            log_channel = self.bot.get_channel(559841284735631365)
            em = discord.Embed(color=ctx.author.color, title="Bug Report")
            em.description = bug
            em.set_footer(text=f"Reported by: {str(ctx.author)} | ID: {ctx.author.id}", icon_url=ctx.author.avatar_url)
            await log_channel.send(embed=em)
            return await ctx.send(f"Your bug report has been sent to the developers to read. Thank you for helping us splat those bugs! {self.bot.get_emoji(511141356769509396)}")
        elif action.lower() == "help":
            msg = f"""
**Welcome to the center of the bug reporting commands!** {self.bot.get_emoji(485250850659500044)}

Here are a list of subcommands you can do within this command:
`*bugs` -> See the list of known bugs that were added by the developers.
`*bugs report [bug description]` -> Found something? Report it to the developers!
`*bugs add [bug description]` -> For devs only: add a bug to the list of known ones.
            """
            return await ctx.send(msg)
        else:
            msg = f"""
**Welcome to the center of the bug reporting commands!** {self.bot.get_emoji(485250850659500044)}

You seem a bit lost, so here are a list of subcommands you can do within this command:
`*bugs` -> See the list of known bugs that were added by the developers.
`*bugs report [bug description]` -> Found something? Report it to the developers!
`*bugs add [bug description]` -> For devs only: add a bug to the list of known ones.
            """
            return await ctx.send(msg)

def setup(bot): 
    bot.add_cog(Info(bot)) 
