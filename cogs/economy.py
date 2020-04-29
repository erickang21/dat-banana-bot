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

    async def balance(self, guild, user):
        x = await self.db.economy.find_one({"id": guild.id})
        guild_users = x["users"]
        return guild_users[str(user.id)]

    async def add_points(self, guild, user, points):
        x = await self.db.economy.find_one({"id": guild.id})
        guild_users = x["users"]
        guild_users[str(user.id)] += points
        await self.db.economy.update_one({"id": guild.id}, {"$set": {"registered": True, "users": guild_users}}, upsert=True)
        

    async def is_registered(self, user):
        x = await self.db.economy.find_one({"user": user.id})
        if x is None:
            return False
        else:
            return True

    async def place_on_cooldown(self, guild, user, cmd):
        """Places the given command on cooldown."""
        data = await self.db.economy.find_one({"id": guild.id})
        guild_user_data = data.get("users")
        match = list(filter(lambda x: x['id'] == user.id, guild_user_data))[0]
        match[cmd] = int(time.time())
        guild_user_data.remove(match)
        guild_user_data.append(match)
        await self.db.economy.update_one({"id": guild.id}, {"$set": {"users": guild_user_data}}, upsert=True)

    async def is_on_cooldown(self, guild, user, cmd):
        """Check if the command is on cooldown."""
        data = await self.db.economy.find_one({"id": guild.id})
        guild_user_data = data.get("users")
        match = list(filter(lambda x: x['id'] == user.id, guild_user_data))[0]
        try:
            cooldown = match[cmd]
        except KeyError:
            return False
        current = int(time.time())
        diff = current - cooldown
        if cmd == "daily_cooldown":
            if diff < 86400:
                return 86400 - diff
            else:
                return False
        elif cmd == "lottery_cooldown" or cmd == "search_cooldown":
            if diff < 60:
                return 60 - diff
            else:
                return False
        elif cmd == "gamble_cooldown":
            if diff < 180:
                return 180 - diff
            else:
                return False
        elif cmd == "rob_cooldown":
            if diff < 300:
                return 300 - diff
            else:
                return False
        elif cmd == "pay_cooldown":
            if diff < 600:
                return 600 - diff
            else:
                return False

    @commands.command()
    @commands.has_permissions(manage_guild = True)
    async def register(self, ctx):
        """Register your server for economy."""
        data = await self.db.economy.find_one({"id": ctx.guild.id})
        if data:
            if data.get("registered", None):
                return await ctx.send("This server is already registered for economy.")
        user_dict = {}
        for user in ctx.guild.members:
            user_dict[str(user.id)] = 0
        await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": user_dict}}, upsert=True)
        await ctx.send(f"Alright! I registered this server for economy. Start earning that money!")

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



    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def deregister(self, ctx):
        """Disable economy for your server."""
        data = await self.db.economy.find_one({"id": ctx.guild.id})
        if data:
            if not data.get("registered", None):
                return await ctx.send("This server's economy is already disabled.", edit=False)
        await ctx.send("""
:warning: **WARNING** :warning:
This will delete ALL data for this server's economy, including everyone's balance, and then disable the commands. 
If you choose to re-enable economy in the future, the data will not be recovered.

**Continue?** (Y/N)

(This automatically cancels in 30 seconds.)""", edit=False
)       
        try:
            x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=30.0)
        except asyncio.TimeoutError:
            return await ctx.send("Timed out.", edit=False)
        if x.content.lower() == "y" or x.content.lower() == "yes":
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": False, "users": []}})
            return await ctx.send(f"I disabled economy for this server. {self.bot.get_emoji(666316667671937034)}", edit=False)
        elif x.content.lower() == "n" or x.content.lower() == "no":
            return await ctx.send("Nope! Economy will still stand.", edit=False)
        else:
            return await ctx.send("INvalid response. Process was cancelled.", edit=False)

        
    @commands.command(aliases=['bal'])
    async def balance(self, ctx, user: discord.Member = None):
        '''Check how much bananas ya got!'''
        user = user or ctx.author
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_users = x["users"]
        person = "You currently have" if not user else f"**{user.name}** currently has"
        em = discord.Embed(color=0x00ff00, title='Current Balance')
        responses = [
            f"{person} **{guild_users[str(ctx.author.id)]}** :banana:. Kinda sad.",
            f"Idk how {person} **{guild_users[str(ctx.author.id)]}** :banana:?!",
            f"REEEEEE! {person} **{guild_users[str(ctx.author.id)]}** :banana:.",
            f"{person} **{guild_users[str(ctx.author.id)]}** :banana:. Man, hella rich.",
            f"{person} **{guild_users[str(ctx.author.id)]}** :banana:. Deal with it.",
            f"{person} **{guild_users[str(ctx.author.id)]}** :banana:. I wonder where this dood's money comes from?!"
        ]
        em.description = random.choice(responses)
        await ctx.send(embed=em)


    @commands.command(aliases=['daily', 'dailyshit'])
    #@commands.cooldown(1, 86400.0, BucketType.user)
    async def dailycredit(self, ctx):
        '''Collect your daily bananas!'''
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_users = x["users"]
        await ctx.trigger_typing()
        async with self.session.get(f"https://discordbots.org/api/bots/520682706896683009/check?userId={ctx.author.id}", headers={'Authorization': self.dbl}) as resp:
            resp = await resp.json()
            if resp['voted'] == 0:
                em = discord.Embed(color=0x00ff00, title='Did you vote for uwu bot today?')
                em.description = """
You can get up to an extra **500** :banana: on **each server you share with me** using daily by simply upvoting dat banana bot on Discord Bot List. 
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
                    await self.add_points(ctx.guild, ctx.author, number)
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
                await self.add_points(ctx.guild, ctx.author, number)
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
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        number = random.randint(0, 500)
        await self.add_points(ctx.guild, ctx.author, number)
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
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_users = x.get("users")
        try:
            amount = int(amount)
        except ValueError:
            return await ctx.send("Please enter a valid number for the amount.")
        if amount <= 0:
            return await ctx.send("Gamble more. Not less. Enter a number more than 0.")
        bal = self.balance(ctx.guild, ctx.author)
        if amount > bal:
            return await ctx.send(f"You gambled WAY TOO MUCH! You currently can gamble up to **{x['points']}** :banana:.")
        choose = random.randint(1, 2)
        if choose == 1:
            await self.add_points(ctx.guild, ctx.author, amount)
            await ctx.send(f"HOORAY! You won **{amount}** :banana:. YEET!")
            await self.place_on_cooldown(ctx.guild, ctx.author, "gamble_cooldown")
        elif choose == 2:
            await self.add_points(ctx.guild, ctx.author, -amount)
            await ctx.send(f"Aw, man! You just lost **{amount}** :banana:. Better luck next time!")
            await self.place_on_cooldown(ctx.guild, ctx.author, "gamble_cooldown")

    @commands.command(alises=['steal'])
    #@commands.cooldown(1, 300, BucketType.user)
    async def rob(self, ctx, user: discord.Member, points: int):
        """Steal from someone else!"""
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        my_points = self.balance(ctx.guild, ctx.author)
        target_points = self.balance(ctx.guild, user)
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
            await self.add_points(ctx.guild, ctx.author, points)
            await self.add_points(ctx.guild, user, -points)
            await ctx.send(f"That was a success! You earned **{points}** :banana:, while that other sucker **{user.name}** lost **{points}** :banana:.")
            await self.place_on_cooldown(ctx.guild, ctx.author, "rob_cooldown")
        elif your_fate == 2:
            await self.add_points(ctx.guild, ctx.author, -points)
            await self.add_points(ctx.guild, user, points)
            await ctx.send(f"That attempt sucked! I mean, thanks for giving **{user.name}** your **{points}** :banana:.")
            await self.place_on_cooldown(ctx.guild, ctx.author, "rob_cooldown")

    @commands.command(alises=['donate'])
    #@commands.cooldown(1, 300, BucketType.user)
    async def pay(self, ctx, user: discord.Member, points: int):
        """Donate credits to someone else!"""
        my_points = self.balance(ctx.guild, ctx.author)
        target_points = self.balance(ctx.guild, user)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x:
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        em = discord.Embed(color=0x00ff00, title='Current Balance')      
        try:
            points = int(points)
        except ValueError:
            return await ctx.send("Please enter a valid number to rob.")
        if points <= 0:
            return await ctx.send("I see you trying to lowkey rob them! Nice try.")
        if points > my_points:
            return await ctx.send(f"Can't donate more than you have. ¯\_(ツ)_/¯ You can donate up to **{my_points}** :banana:.")
        await self.add_points(ctx.guild, ctx.author, -points)
        await self.add_points(ctx.guild, user, points)
        await ctx.send(f"Thanks for being generous! **{user.name}** now has **{points}** :banana: more, thanks to you. :thumbsup:")
        
        
    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        """Get the leaderboard for economy!"""
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        users = x.get("users")
        lb = ""
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Economy(bot))
