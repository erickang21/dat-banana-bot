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


class Economy:
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.session
        self.db = self.bot.db
        self.dbl = self.bot.config.dbl
        self.lottery_numbers = [str(random.randint(0, 9)), str(random.randint(0, 9)), str(random.randint(0, 9))]

    def dev_check(self, id):
        with open('data/devs.json') as f:
            devs = json.load(f)
            if id in devs:
                return True
        return False

    async def add_points(self, guild, user, points):
        x = await self.db.economy.find_one({"id": guild.id})

        #total = int(x['points']) + points
        #await self.db.economy.update_one({"user": user.id}, {"$set": {"points": int(total)}}, upsert=True)
        guild_user_data = x.get("users")
        match = list(filter(lambda x: x['id'] == user.id, guild_user_data))[0]
        match['points'] += points 
        guild_user_data.remove(match)
        guild_user_data.append(match)
        await self.db.economy.update_one({"id": guild.id}, {"$set": {"users": guild_user_data}}, upsert=True)
        

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
        elif cmd == "lottery_cooldown":
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

    @commands.command()
    @commands.has_permissions(manage_guild = True)
    async def register(self, ctx):
        """Register your server for economy."""
        data = await self.db.economy.find_one({"id": ctx.guild.id})
        if data:
            if data.get("registered", None):
                return await ctx.send("This server is already registered for economy.")
        await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        await ctx.send(f"Alright! I registered this server for economy. Start earning that money!")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def deregister(self, ctx):
        """Disable economy for your server."""
        data = await self.db.economy.find_one({"id": ctx.guild.id})
        if data:
            if not data.get("registered", None):
                return await ctx.send("This server's economy is already disabled.")
        await ctx.send("""
:warning: **WARNING** :warning:
This will delete ALL data for this server's economy, including everyone's balance, and then disable the commands. 
If you choose to re-enable economy in the future, the data will not be recovered.

**Continue?** (Y/N)

(This automatically cancels in 30 seconds.)"""
)       
        try:
            x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=30.0)
        except asyncio.TimeoutError:
            return await ctx.send("Timed out.")
        if x.content.lower() == "y" or x.content.lower() == "yes":
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": False, "users": []}})
            return await ctx.send(f"Okay, I disabled economy for this server. :cry:")
        elif x.content.lower() == "n" or x.content.lower() == "no":
            return await ctx.send("Nope! Economy will still stand.")
        else:
            return await ctx.send("INvalid response. Process was cancelled.")

    @commands.command(aliases=['openbank'])
    async def openaccount(self, ctx):
        '''Opens a bank account for the economy!'''
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x:
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
            x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x.get("registered", True):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_user_data = x.get("users")
        user_ids = list(map(lambda a: a['id'], guild_user_data))
        if ctx.author.id in user_ids:
            return await ctx.send(f"You already have a bank account in **{guild_name}**.")
        user_data = {
            "id": ctx.author.id,
            "points": 0
        }
        guild_user_data.append(user_data)
        await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": guild_user_data}}, upsert=True)
        
        await ctx.send(f"Your bank account is now open for **{guild_name}**.")


        
    @commands.command(aliases=['bal'])
    async def balance(self, ctx, user: discord.Member = None):
        '''Check how much bananas ya got!'''
        user = user or ctx.author
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x: 
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_user_data = x.get("users")
        user_ids = list(map(lambda a: a['id'], guild_user_data))
        person = "You currently have" if not user else f"**{user.name}** currently has"
        
        em = discord.Embed(color=0x00ff00, title='Current Balance')
        try:
            match = list(filter(lambda x: x['id'] == user.id, guild_user_data))[0]
        except IndexError:
            em.description = f"{person} don't have an account in **{guild_name}** yet! Open one using `*openaccount`."
        else:
            responses = [
                f"{person} **{match['points']}** :banana:. Kinda sad.",
                f"Idk how {person} **{match['points']}** :banana:?!",
                f"REEEEEE! {person} **{match['points']}** :banana:.",
                f"{person} **{match['points']}** :banana:. Man, hella rich.",
                f"{person} **{match['points']}** :banana:. Deal with it.",
                f"{person} **{match['points']}** :banana:. I wonder where this dood's money comes from?!"
            ]
            em.description = random.choice(responses)
        await ctx.send(embed=em)


    @commands.command(aliases=['daily', 'dailyshit'])
    #@commands.cooldown(1, 86400.0, BucketType.user)
    async def dailycredit(self, ctx):
        '''Collect your daily bananas!'''
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x: 
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_user_data = x.get("users")
        user_ids = list(map(lambda a: a['id'], guild_user_data))
        em = discord.Embed(color=0x00ff00, title='Current Balance')
        try:
            match = list(filter(lambda x: x['id'] == ctx.author.id, guild_user_data))[0]
        except IndexError:
            return await ctx.send(f"You don't have an account in **{guild_name}** yet! Open one using `*openaccount`.")
        await ctx.trigger_typing()
        check = await self.is_on_cooldown(ctx.guild, ctx.author, "daily_cooldown")
        if check:
            minute, second = divmod(check, 60)
            hour, minute = divmod(minute, 60)
            if hour:
                time_left = f"{hour}:{Utils.format_time(minute)}:{Utils.format_time(second)}"
            else:
                time_left = f"{minute}:{Utils.format_time(second)}"
            return await ctx.send(f"C'mon, asking ahead of time? Patience, man.\n\n:timer: **Time Left:**\n{time_left}")
        async with self.session.get(f"https://discordbots.org/api/bots/388476336777461770/check?userId={ctx.author.id}", headers={'Authorization': self.dbl}) as resp:
            resp = await resp.json()
            if resp['voted'] == 0:
                em = discord.Embed(color=0x00ff00, title='Did you vote for dat banana bot today?')
                em.description = """
You can get up to an extra **500** :banana: on **each server you share with me** using daily by simply upvoting dat banana bot on Discord Bot List. 
Click [here](https://discordbots.org/bot/388476336777461770/vote) to vote now.

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
                    guild_name = await Utils.clean_text(ctx, ctx.guild.name)
                    x = await self.db.economy.find_one({"id": ctx.guild.id})
                    if not x: 
                        await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
                    if not x.get("registered"):
                        return await ctx.send("Sorry, but the server's economy commands have been disabled.")
                    guild_user_data = x.get("users")
                    user_ids = list(map(lambda a: a['id'], guild_user_data))
                    em = discord.Embed(color=0x00ff00, title='Current Balance')
                    try:
                        match = list(filter(lambda x: x['id'] == ctx.author.id, guild_user_data))[0]
                    except IndexError:
                        return await ctx.send(f"You don't have an account in **{guild_name}** yet! Open one using `*openaccount`.")
                    else:
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
                        await self.place_on_cooldown(ctx.guild, ctx.author, "daily_cooldown")
                        return await ctx.send(random.choice(responses))
                elif reaction.emoji == '❌':
                    return await ctx.send("ALRIGHT! That's what I'm talking about. The link is above, now go and show me some love! :D")
            else:
                number = random.randint(800, 1000)
                guild_name = await Utils.clean_text(ctx, ctx.guild.name)
                x = await self.db.economy.find_one({"id": ctx.guild.id})
                if not x: 
                    await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
                if not x.get("registered"):
                    return await ctx.send("Sorry, but the server's economy commands have been disabled.")
                guild_user_data = x.get("users")
                user_ids = list(map(lambda a: a['id'], guild_user_data))
                em = discord.Embed(color=0x00ff00, title='Current Balance')
                try:
                    match = list(filter(lambda x: x['id'] == ctx.author.id, guild_user_data))[0]
                except IndexError:
                    return await ctx.send(f"You don't have an account in **{guild_name}** yet! Open one using `*openaccount`.")
                else:
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
                    await self.place_on_cooldown(ctx.guild, ctx.author, "daily_cooldown")
                    return await ctx.send(random.choice(responses))
        

        

    @commands.command()
    async def lottery(self, ctx, numbers: str):
        '''Enter the lottery to win/lose! 3 numbers, seperate with commas. Entry is $50, winner gets $10 million!'''
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x:
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_user_data = x.get("users")
        user_ids = list(map(lambda a: a['id'], guild_user_data))
        em = discord.Embed(color=0x00ff00, title='Current Balance')
        try:
            match = list(
                filter(lambda x: x['id'] == ctx.author.id, guild_user_data))[0]
        except IndexError:
            return await ctx.send(f"You don't have an account in **{guild_name}** yet! Open one using `*openaccount`.")
        check = await self.is_on_cooldown(ctx.guild, ctx.author, "lottery_cooldown")
        if check:
            minute, second = divmod(check, 60)
            hour, minute = divmod(minute, 60)
            if hour:
                time_left = f"{hour}:{Utils.format_time(minute)}:{Utils.format_time(second)}"
            else:
                time_left = f"{minute}:{Utils.format_time(second)}"
            return await ctx.send(f"C'mon, asking ahead of time? Patience, man.\n\n:timer: **Time Left:**\n{time_left}")
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x: 
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_user_data = x.get("users")
        user_ids = list(map(lambda a: a['id'], guild_user_data))
        em = discord.Embed(color=0x00ff00, title='Current Balance')
        try:
            match = list(filter(lambda x: x['id'] == ctx.author.id, guild_user_data))[0]
        except IndexError:
            return await ctx.send(f"You don't have an account in **{guild_name}** yet! Open one using `*openaccount`.")
        else:
        
            if match['points'] < 100:
                return await ctx.send("Entering the lottery requires 100 :banana:. You don't have enough! Keep on earning 'em")
            if numbers is None:
                return await ctx.send("Please enter 3 numbers seperated by commas to guess the lottery! \nExample: *lottery 1,2,3")
            numbers = numbers.replace(' ', '')
            numbers = numbers.split(',')
            #lucky = [str(random.randint(0, 9)), str(random.randint(0, 9)), str(random.randint(0, 9))]
            for i in numbers:
                try:
                    int(i)
                except ValueError:
                    return await ctx.send("Please enter only numbers for the lottery!")
            lol = ""
            for x in self.lottery_numbers:
                lol += f"`{x}` "
            if numbers == self.lottery_numbers:
                responses = [
                    "Bruh. Just how...",
                    "Y'know only 0.8% people can even get to see this.",
                    "I'm gonna be SO BROKE!",
                    "Take it. Don't even look at me...",
                    "You just...WON?",
                    "Could I be dreaming this?"
                ]
                await self.add_points(ctx.guild, ctx.author, 10000000)
                em = discord.Embed(color=0x00ff00, title='You are the lucky winner!')
                em.description = f'{random.choice(responses)} :tada:\n\nYou won 10,000,000 :banana:!'
                await ctx.send(embed=em)
                self.lottery_numbers = [str(random.randint(0, 9)), str(random.randint(0, 9)), str(random.randint(0, 9))]
                await self.place_on_cooldown(ctx.guild, ctx.author, "lottery_cooldown")
            else:
                await self.add_points(ctx.guild, ctx.author, -100)
                em = discord.Embed(color=0xf44e42)
                responses = [
                    f"OOF! Guess who didn't win the giant $$ this time!",
                    "Aw, try again!",
                    "Yo luck really succs...",
                    "Cry all you want, but you ain't gonna get that 10,000,000 :banana:.",
                    "Well, I ain't gonna stick around and waste time on someone who didn't win...",
                    "And the bad luck goes SKRRRRRRA!",
                    "Guess you're part of the 99.2% that didn't make it."
                ]
                em.description = f"{random.choice(responses)} ¯\_(ツ)_/¯\n\nYou lost: 100 :banana:"
                await ctx.send(embed=em)
                await self.bot.get_channel(445332002942484482).send(f"The winning numbers are: {self.lottery_numbers}")
                await self.place_on_cooldown(ctx.guild, ctx.author, "lottery_cooldown")

    @commands.command(aliases=['bet'])
    #@commands.cooldown(1, 300, BucketType.user)
    async def gamble(self, ctx, amount):
        """Choose an amount. Will you win it or will you lose it?"""
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x:
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_user_data = x.get("users")
        user_ids = list(map(lambda a: a['id'], guild_user_data))
        em = discord.Embed(color=0x00ff00, title='Current Balance')
        try:
            match = list(
                filter(lambda x: x['id'] == ctx.author.id, guild_user_data))[0]
        except IndexError:
            return await ctx.send(f"You don't have an account in **{guild_name}** yet! Open one using `*openaccount`.")
        check = await self.is_on_cooldown(ctx.guild, ctx.author, "gamble_cooldown")
        if check:
            minute, second = divmod(check, 60)
            hour, minute = divmod(minute, 60)
            if hour:
                time_left = f"{hour}:{Utils.format_time(minute)}:{Utils.format_time(second)}"
            else:
                time_left = f"{minute}:{Utils.format_time(second)}"
            return await ctx.send(f"C'mon, asking ahead of time? Patience, man.\n\n:timer: **Time Left:**\n{time_left}")
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x:
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_user_data = x.get("users")
        user_ids = list(map(lambda a: a['id'], guild_user_data))
        try:
            match = list(
                filter(lambda x: x['id'] == ctx.author.id, guild_user_data))[0]
        except IndexError:
            return await ctx.send(f"You don't have an account in **{guild_name}** yet! Open one using `*openaccount`.")
        else:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.send("Please enter a valid number for the amount.")
            if amount <= 0:
                return await ctx.send("Gamble more. Not less. Enter a number more than 0.")
            if amount > match['points']:
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
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x:
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_user_data = x.get("users")
        user_ids = list(map(lambda a: a['id'], guild_user_data))
        em = discord.Embed(color=0x00ff00, title='Current Balance')
        try:
            match = list(
                filter(lambda x: x['id'] == ctx.author.id, guild_user_data))[0]
        except IndexError:
            return await ctx.send(f"You don't have an account in **{guild_name}** yet! Open one using `*openaccount`.")
        check = await self.is_on_cooldown(ctx.guild, ctx.author, "rob_cooldown")
        if check:
            minute, second = divmod(check, 60)
            hour, minute = divmod(minute, 60)
            if hour:
                time_left = f"{hour}:{Utils.format_time(minute)}:{Utils.format_time(second)}"
            else:
                time_left = f"{minute}:{Utils.format_time(second)}"
            return await ctx.send(f"C'mon, asking ahead of time? Patience, man.\n\n:timer: **Time Left:**\n{time_left}")
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x: 
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_user_data = x.get("users")
        user_ids = list(map(lambda a: a['id'], guild_user_data))
        em = discord.Embed(color=0x00ff00, title='Current Balance')
        try:
            you = list(filter(lambda x: x['id'] == ctx.author.id, guild_user_data))[0]
        except IndexError:
            return await ctx.send(f"You don't have an account in **{guild_name}** yet! Open one using `*openaccount`.")
        try:
            other = list(
                filter(lambda x: x['id'] == user.id, guild_user_data))[0]
        except IndexError:
            return await ctx.send(f"**{user.name}** doesn't have an account in **{guild_name}** yet! Open one using `*openaccount`.")
        else:      
            try:
                points = int(points)
            except ValueError:
                return await ctx.send("Please enter a valid number to rob.")
            if points <= 0:
                return await ctx.send("Trying to rob less than 0? I think not.")
            if points > you['points']:
                return await ctx.send(f"Can't rob more than you have. ¯\_(ツ)_/¯ You can rob up to **{you['points']}** :banana:.")
            if points > other['points']:
                return await ctx.send(f"Can't rob more than **{user.name}** has. ¯\_(ツ)_/¯ You can rob up to **{other['points']}** :banana:.")
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

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        """Get the leaderboard for economy!"""
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x:
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        users = x.get("users")
        lb = ""
        counter = 0
        points = sorted(list(map(lambda x: x['points'], users)), reverse=True)
        for point in points:
            counter += 1
            lb += f"**{str(self.bot.get_user(list(filter(lambda a: a['points'] == point, users))[0]['id']))}:** {point}\n"
            if counter == 10:
                break
        em = discord.Embed(color=0x00ff00, title="Economy Leaderboard")
        em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        em.description = lb

        await ctx.send(embed=em)



    @commands.command(aliases=['give'], hidden=True)
    @commands.has_permissions(manage_guild=True)
    async def reward(self, ctx, user: discord.Member, points):
        '''Reward a good person'''
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x:
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_user_data = x.get("users")
        user_ids = list(map(lambda a: a['id'], guild_user_data))
        if user.id not in user_ids:
            return await ctx.send(f"ACK! **{str(user)}** doesn't have an account yet, so they can't get the gucci money!")
        else:
            try:
                points = int(points)
            except ValueError:
                return await ctx.send("ACK! Please enter a valid number for points.")
            try:
                await self.add_points(ctx.guild, user, points)
                await ctx.send(f"YEET! Added **{points}** :banana: to **{str(user)}**!")
            except Exception as e:
                await ctx.send(f"Oops, something went wrong. ```{e}```Please report to the developers!")
                print(e)

    @commands.command(aliases=['remove'],hidden=True)
    @commands.has_permissions(manage_guild=True)
    async def deduct(self, ctx, user: discord.Member, points):
        '''Fines a bad boi.'''
        guild_name = await Utils.clean_text(ctx, ctx.guild.name)
        x = await self.db.economy.find_one({"id": ctx.guild.id})
        if not x:
            await self.db.economy.update_one({"id": ctx.guild.id}, {"$set": {"registered": True, "users": []}}, upsert=True)
        if not x.get("registered"):
            return await ctx.send("Sorry, but the server's economy commands have been disabled.")
        guild_user_data = x.get("users")
        user_ids = list(map(lambda a: a['id'], guild_user_data))
        if user.id not in user_ids:
            return await ctx.send(f"ACK! **{str(user)}** doesn't have an account yet, so you can't take away money from them!")
        else:
            try:
                points = int(points)
            except ValueError:
                return await ctx.send("ACK! Please enter a valid number for points.")
            try:
                await self.add_points(ctx.guild, user, -points)
                await ctx.send(f"OOF! Removed **{points}** :banana: to **{str(user)}**!")
            except Exception as e:
                await ctx.send(f"Oops, something went wrong. ```{e}```Please report to the developers!")
                print(e)


def setup(bot):
    bot.add_cog(Economy(bot))
