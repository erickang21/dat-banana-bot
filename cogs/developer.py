import discord
import sys
import os
import io
import pip
import asyncio
import aiohttp
import random
import subprocess
import json
import ezjson
from discord.ext import commands


class Developer:
    def __init__(self, bot):
       self.bot = bot


    def dev_check(self, id):
        with open('data/devs.json') as f:
            devs = json.load(f)
            if id in devs:
                return True
        return False


    def owner_check(self, id):
        if id == 277981712989028353:
            return True
        return False
       
       
       
    @commands.command()
    async def restart(self, ctx):
        """Makes the bot shut UP and then shut DOWN, then start up again."""
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        msg = await ctx.send("Shutting down...")
        await asyncio.sleep(1)
        await msg.edit(content="Goodbye! :wave:")
        await bot.logout()
        
        
    @commands.command()
    async def changename(self, ctx, name=None):
        """Changes my name. Please make it good!"""
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        if name is None:
            return await ctx.send("Hmm...my name cannot be blank!")
        else:
            await self.bot.user.edit(username=f'name')


    @commands.command()
    async def exec(self, ctx, code):
        """Executes code like the Command Line."""
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        await ctx.send(subprocess.run(f"{code}", cwd='/Users/Administrator/dat-banana-bot', stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8'))


    @commands.command()
    async def update(self, ctx):
        """Updates the bot. Ez!"""
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        try:
            lol = subprocess.run("git pull", cwd='/Users/Administrator/dat-banana-bot', stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
            for cog in self.bot.cogs:
                self.bot.unload_extension(f"cogs.{cog}")
                self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"All cogs reloaded, and READY TO ROLL! :white_check_mark: \n\nLog:\n```{lol}```")
        except Exception as e:
            await ctx.send(f"An error occured. :x: \n\nDetails: \n{e}")


              

    @commands.command()
    async def blacklist(self, ctx, user: discord.Member):
        if not self.owner_check(ctx.author.id):
            await ctx.send("DON'T BE SHADY... :eyes:\nThis command is owner only. :x:")
        else:
            ezjson.dump("data/blacklist.json", ctx.author.id, True)
            await ctx.send("Success. :white_check_mark: The user is now put on the blacklist. :smiling_imp: ")


def setup(bot): 
    bot.add_cog(Developer(bot))   
    
