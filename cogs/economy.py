import discord
import sys
import os
import io
import json
import time
import ezjson
import random
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from .utils.utils import Utils


class Error(Exception):
    pass


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.session
        self.db = self.bot.db
        self.dbl = self.bot.config.dbl
        self.lottery_numbers = [str(random.randint(0, 9)), str(random.randint(0, 9)), str(random.randint(0, 9))]
        self.cooldowns = {}

    def dev_check(self, id):
        with open('data/devs.json') as f:
            devs = json.load(f)
            if id in devs:
                return True
        return False
    

    async def balance(self, ctx):
        data = await self.db.economy.find_one({"guild": ctx.guild.id, "user": ctx.author.id})
        bal = 0
        if data:
            bal = data["points"]
        return bal

    async def add_points(self, ctx, points):
        data = await self.db.economy.find_one({"guild": ctx.guild.id, "user": ctx.author.id})
        if data:
            data["points"] += points
        else:
            data = {
                "points": points,
                "daily": 0,
                "level": 0
            } 
        await self.db.economy.update_one({"guild": ctx.guild.id, "user": ctx.author.id}, {"$set": data}, upsert=True)
     
    async def place_on_cooldown(self, ctx):
        data = await self.db.economy.find_one({"guild": ctx.guild.id, "user": ctx.author.id})
        if data:
            data["daily"] = ctx.message.created_at.timestamp() + 8640000
        else:
            data = {
                "points": 0,
                "daily": ctx.message.created_at.timestamp() + 8640000,
                "level": 0
            } 
        await bot.db.cooldowns.update_one({"id": ctx.guild.id}, {"$set": data}, upsert=True)

    def fmt_time(self, time):
        if time < 3600:
            minutes = time // 60
            seconds = time - minutes * 60
            if 0 <= seconds <= 9:
                seconds = "0" + str(seconds)
            return f"{minutes} minutes, {seconds} seconds"
        else:
            hours = time // 3600
            minutes = (time - hours * 3600) // 60
            seconds = time - hours * 3600 - minutes * 60
            return f"{hours} hours, {minutes} minutes, {seconds} seconds"

    async def time_left(self, ctx):
        data = await self.db.economy.find_one({"guild": ctx.guild.id, "user": ctx.author.id})
        cooldown = 0
        current_time = ctx.message.created_at.timestamp()
        if data:
            if current_time < data["daily"]:
                cooldown = data["daily"] - current_time
        return cooldown if not cooldown else self.fmt_time(cooldown)

    @commands.command()
    @commands.has_permissions(manage_guild = True)
    async def levelup(self, ctx, action=""):
        """Enable level up tracking and messages for the server."""
        data = await self.db.level.find_one({"id": ctx.guild.id})
        if action.lower() == "on":
            if data["enabled"]:
                return await ctx.send("Level-up has already been enabled for this server.")
            else:
                user_dict = {}
                for x in ctx.guild.members:
                    user_dict[str(x.id)] = 0
                await self.db.level.update_one({"id": ctx.guild.id}, {"$set": {"enabled": True, "users": user_dict}})
                return await ctx.send(f"Level-up is now enabled for this server. {self.bot.get_emoji(484897652220362752)}")
        elif action.lower() == "off":
            if not data["enabled"]:
                return await ctx.send("Level-up has been already disabled for this server.")
            else:
                user_dict = data["users"]
                await self.db.level.update_one({"id": ctx.guild.id}, {"$set": {"enabled": False, "users": user_dict}})
                return await ctx.send(f"Level-up is now disabled for this server. {self.bot.get_emoji(666316667671937034)}")
        else:
            if data["enabled"]:
                return await ctx.send("Level-up is currently **enabled!** (You can disable it by running `uwu levelup off`.)")
            else:
                return await ctx.send("Level-up is currently **disabled.** (You can enable it by running `uwu levelup on`.)")
        
    @commands.command(aliases=['bal'])
    async def balance(self, ctx, user: discord.Member = None):
        '''Check how much bananas ya got!'''
        if user:
            ctx.author = user
        bal = self.balance(ctx)
        person = "You currently have" if not user else f"**{user.name}** currently has"
        em = discord.Embed(color=0x00ff00, title='Current Balance')
        responses = [
            f"{person} **{bal}** :banana:. Kinda sad.",
            f"Idk how {person} **{bal}** :banana:?!",
            f"REEEEEE! {person} **{bal}** :banana:.",
            f"{person} **{bal}** :banana:. Man, hella rich.",
            f"{person} **{bal}** :banana:. Deal with it.",
            f"{person} **{bal}** :banana:. I wonder where this dood's money comes from?!"
        ]
        em.description = random.choice(responses)
        await ctx.send(embed=em)


    @commands.command(aliases=['daily', 'dailyshit'])
    #@commands.cooldown(1, 86400.0, BucketType.user)
    async def dailycredit(self, ctx):
        '''Collect your daily bananas!'''
        await ctx.trigger_typing()
        async with self.session.get(f"https://discordbots.org/api/bots/520682706896683009/check?userId={ctx.author.id}", headers={'Authorization': self.dbl}) as resp:
            resp = await resp.json()
            if resp['voted'] == 0:
                em = discord.Embed(color=0x00ff00, title='Did you vote for uwu bot today?')
                em.description = """
You can get up to an extra **500** :banana: on **each server you share with me** using daily by simply upvoting uwu bot on Discord Bot List. 
Click [here](https://discordbots.org/bot/520682706896683009/vote) to vote now.

__What to do now?__
:white_check_mark:: Receive your reduced daily credit and move on.
:x:: Be a good boi and go upvote. 

**Note:** DBL takes some time to process upvotes. If you upvoted, please wait a few minutes and then retry this command.
"""
                msg = await ctx.send(embed=em)
                await msg.add_reaction("\U00002705")
                await msg.add_reaction("\U0000274c")
                reaction, user = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author)
                if reaction.emoji == '✅':
                    number = random.randint(300, 500)
                    await self.add_points(ctx, number)
                    await self.place_on_cooldown(ctx)
                    responses = [
                        f"Be proud. You just got **{number}** :banana:.",
                        f"*Why u ask me for da MONEY?* Anyways, you got **{number}** :banana:.",
                        f"Ugh fine, take my money. But only **{number}** :banana:.",
                        f"Why would you ever rob a poor man? Fine, take **{number}** :banana:.",
                        f"You can have **{number}** :banana:, if that means you can shut up.",
                        f"If you take **{number}** :banana:, ur mom gay. Oh well, you did :rofl:",
                        f"I'd hate to give away **{number}** :banana:, but it's in my programming...",
                        f"I love all my bananas. You just *had*  to take away **{number}** :banana: from me..."
                    ]
                    return await ctx.send(random.choice(responses))
                elif reaction.emoji == '❌':
                    return await ctx.send("Thank you so much! Upvote me here :)\n\nhttps://discordbots.org/bot/520682706896683009/vote")
            else:
                number = random.randint(800, 1000)
                await self.add_points(ctx, number)
                await self.place_on_cooldown(ctx)
                responses = [
                    f"Be proud. You just got **{number}** :banana:.",
                    f"*Why u ask me for da MONEY?* Anyways, you got **{number}** :banana:.",
                    f"Ugh fine, take my money. But only **{number}** :banana:.",
                    f"Why would you ever rob a poor man? Fine, take **{number}** :banana:.",
                    f"You can have **{number}** :banana:, if that means you can shut up.",
                    f"If you take **{number}** :banana:, ur mom gay. Oh well, you did :rofl:",
                    f"I'd hate to give away **{number}** :banana:, but it's in my programming...",
                    f"I love all my bananas. You just *had*  to take away **{number}** :banana: from me..."
                ]
                return await ctx.send(random.choice(responses))
        
    @commands.command()
    #@commands.cooldown(1, 60.0, BucketType.user)
    async def search(self, ctx):
        """A way to earn currency."""
        number = random.randint(0, 500)
        await self.add_points(ctx, number)
        zero_responses = [
            f"You tried so hard but you couldn't succeed. {self.bot.get_emoji(522530579627900938)}",
            f"Mission FAILED! {self.bot.get_emoji(522530579627900938)}",
            f"People around here have big brains. No money for you! {self.bot.get_emoji(522530579627900938)}",
            f"Nice try, you gold digger. {self.bot.get_emoji(522530579627900938)}"
        ]
        responses = [
            f"uwu you just found **{number}** :banana:.",
            f"You lucky human. **{number}** :banana: is yours.",
            f"You found **{number}**:banana: under your sleeping mom.",
            f"You fished in your dad's wallet for **{number}** :banana:.",
            f"You dug out a red pocket with **{number}** :banana:.",
            f"**{number}** :banana: came falling from the sky. And with the sky.",
            f"My personal gift, **{number}** :banana: to you.",
            f"You picked up **{number}** :banana: from the toilet."
        ]
        if number == 0:
            return await ctx.send(random.choice(zero_responses))
        else:
            return await ctx.send(random.choice(responses))
        
    @commands.command(aliases=['bet'])
    #@commands.cooldown(1, 300, BucketType.user)
    async def gamble(self, ctx, amount):
        """Choose an amount. Will you win it or will you lose it?"""
        try:
            amount = int(amount)
        except ValueError:
            return await ctx.send("Please enter a valid number for the amount.")
        if amount <= 0:
            return await ctx.send("Gamble more. Not less. Enter a number more than 0.")
        bal = self.balance(ctx)
        if amount > bal:
            return await ctx.send(f"You gambled WAY TOO MUCH! You currently can gamble up to **{bal}** :banana:.")
        choose = random.randint(1, 2)
        if choose == 1:
            await self.add_points(ctx, amount)
            await ctx.send(f"HOORAY! You won **{amount}** :banana:. YEET!")
        elif choose == 2:
            await self.add_points(ctx, -amount)
            await ctx.send(f"Aw, man! You just lost **{amount}** :banana:. Better luck next time!")

    @commands.command(alises=['steal'])
    #@commands.cooldown(1, 300, BucketType.user)
    async def rob(self, ctx, user: discord.Member, points: int):
        """Steal from someone else!"""
        my_points = self.balance(ctx)
        temp = ctx.author
        ctx.author = user
        target_points = self.balance(ctx)
        ctx.author = temp
        try:
            points = int(points)
        except ValueError:
            return await ctx.send("Please enter a valid number to rob.")
        if points <= 0:
            return await ctx.send("Trying to rob less than 0? I think not.")
        if points > my_points:
            return await ctx.send(f"Can't rob more than you have. ¯\_(ツ)_/¯ You can rob up to **{my_points}** :banana:.")
        if points > target_points:
            return await ctx.send(f"Can't rob more than **{user.name}** has. ¯\_(ツ)_/¯ You can rob up to **{target_points}** :banana:.")
        your_fate = random.randint(1, 2)
        if your_fate == 1:
            await self.add_points(ctx, points)
            temp = ctx.author
            ctx.author = user
            await self.add_points(ctx, -points)
            ctx.author = temp
            await ctx.send(f"That was a success! You earned **{points}** :banana:, while that other sucker **{user.name}** lost **{points}** :banana:.")
        elif your_fate == 2:
            await self.add_points(ctx, points)
            temp = ctx.author
            ctx.author = user
            await self.add_points(ctx, -points)
            ctx.author = temp
            await ctx.send(f"That attempt sucked! I mean, thanks for giving **{user.name}** your **{points}** :banana:.")

    @commands.command(alises=['donate'])
    #@commands.cooldown(1, 300, BucketType.user)
    async def pay(self, ctx, user: discord.Member, points):
        """Donate credits to someone else!"""
        my_points = self.balance(ctx)    
        try:
            points = int(points)
        except ValueError:
            return await ctx.send("Please enter a valid number to donate.")
        if points <= 0:
            return await ctx.send("I see you trying to lowkey rob them! Nice try.")
        if points > my_points:
            return await ctx.send(f"Can't donate more than you have. ¯\_(ツ)_/¯ You can donate up to **{my_points}** :banana:.")
        await self.add_points(ctx, -points)
        ctx.author = user
        await self.add_points(ctx, points)
        await ctx.send(f"Thanks for being generous! **{user.name}** now has **{points}** :banana: more, thanks to you. :thumbsup:")
        
        
    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        """Get the leaderboard for economy!"""
        
        lb = ""
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Economy(bot))
