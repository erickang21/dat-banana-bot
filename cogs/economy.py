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
    
    async def level(self, ctx):
        data = await self.db.economy.find_one({"guild": ctx.guild.id, "user": ctx.author.id})
        level = 0
        if data:
            level = data["level"]
        return level

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
            data["daily"] = ctx.message.created_at.timestamp() + 86400
        else:
            data = {
                "points": 0,
                "daily": ctx.message.created_at.timestamp() + 86400,
                "level": 0
            } 
        await self.db.economy.update_one({"guild": ctx.guild.id, "user": ctx.author.id}, {"$set": data}, upsert=True)

    def fmt_time(self, time):
        if time < 3600:
            minutes = time // 60
            seconds = time - minutes * 60
            if 0 <= seconds <= 9:
                seconds = "0" + str(seconds)
            return f"{minutes} minutes, {seconds} seconds"
        else:
            hours = int(time // 3600)
            minutes = int((time - hours * 3600) // 60)
            seconds = int(time - hours * 3600 - minutes * 60)
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
    
    @commands.command()
    async def shop(self, ctx, action=None, item=None):
        """View the role shop."""
        if not action and not item:
            data = await self.db.shop.find_one({"id": ctx.guild.id})
            em = discord.Embed(color=ctx.author.color, title=ctx.guild.name)
            em.set_author(name="Role Shop", icon_url=ctx.guild.icon_url)
            desc = ""
            if not data:
                desc = "This server does not have any roles yet!"
            else:
                data.pop("_id")
                data.pop("id")
                for role in data:
                    desc += "`" + str(role) + "` ❯ " + str(data[role]) + " :banana:\n" 
            em.description = desc
            await ctx.send(embed=em)
        elif action.lower() == "add":
            if not ctx.author.guild_permissions.manage_guild:
                return await ctx.send("You have insufficient permissions to run this command.", edit=False)
            await ctx.send("Please send the **name** of the role you wish to add to the shop.", edit=False)
            try:
                name = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
            except asyncio.TimeoutError:
                return await ctx.send("Request timed out. Please run this command again.", edit=False)
            name = name.content
            await ctx.send(f"Please send the **price** (:banana:) members should pay for the **{name}** role.", edit=False)
            try:
                price = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
            except asyncio.TimeoutError:
                return await ctx.send("Request timed out. Please run this command again.", edit=False)
            if name not in [x.name for x in ctx.guild.roles]:
                return await ctx.send("Invalid role name entered. Please run this command again.", edit=False)
            try:
                price = int(price.content)
            except:
                return await ctx.send("Invalid price entered. Please run this command again.", edit=False)
            roles = await self.db.shop.find_one({"id": ctx.guild.id})
            if not roles:
                roles = {}
            roles[name] = price
            await self.db.shop.update_one({"id": ctx.guild.id}, {"$set": roles}, upsert=True)
            await ctx.send(f"I have successfully added the **{name}** role to the server's shop, selling for **{price}** :banana:.")
        elif action.lower() == "remove":
            if not ctx.author.guild_permissions.manage_guild:
                return await ctx.send("You have insufficient permissions to run this command.", edit=False)
            await ctx.send("Please send the **name** of the role you wish to remove from the shop.", edit=False)
            try:
                name = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
            except asyncio.TimeoutError:
                return await ctx.send("Request timed out. Please run this command again.", edit=False)
            name = name.content
            if name not in [x.name for x in ctx.guild.roles]:
                return await ctx.send("Invalid role name entered. Please run this command again.", edit=False)
            roles = await self.db.shop.find_one({"id": ctx.guild.id})
            if not roles:
                return await ctx.send("You do not have a role shop set up yet!", edit=False)
            if not roles.get(name, None):
                return await ctx.send("This role is not in the list of roles! Please run this command again.", edit=False)
            await ctx.send(f"{self.bot.get_emoji(704757111493754880)} **Are you certain?** {self.bot.get_emoji(704757111493754880)}\n\nThis will remove the **{name}** role from the shop (cost is **{roles[name]}** :banana:). (Y/N)")
            try:
                response = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
            except asyncio.TimeoutError:
                return await ctx.send("Request timed out. Please run this command again.", edit=False)
            response = response.content
            if response.lower() == "y":
                roles.pop(name)
                await self.db.shop.update_one({"id": ctx.guild.id}, {"$set": roles})
                return await ctx.send(f"The role **{name}** was successfully removed from the shop. :wastebasket:", edit=False)
            else:
                return await ctx.send("The operation has been cancelled.", edit=False)
        elif action.lower() == "buy":
            if not item:
                return await ctx.send("Please specify the item you wish to buy.", edit=False)
            roles = await self.db.shop.find_one({"id": ctx.guild.id})
            if item not in roles.keys():
                return await ctx.send("This role is not in the list of roles on sale! Please do `uwu shop` to find this list.", edit=False)
            await ctx.send(f"**ARE YOU SURE?**\n\nYou are about to buy the **{item}** role for **{roles[item]}** :banana:. (Y/N)", edit=False)
            try:
                response = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
            except asyncio.TimeoutError:
                return await ctx.send("Request timed out. Please run this command again.", edit=False)
            response = response.content
            if response.lower() == "y":
                bal = await self.balance(ctx)
                if balance < roles[item]:
                    return await ctx.send("You do not have enough credits to buy this!")
                await self.add_points(ctx, -roles[item])
                await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name=item))
                await ctx.send(f"Congratulations! You have successfully purchased the **{item}** role. {self.bot.get_emoji(690208316336767026)}", edit=False)
            elif response.lower() == "n":
                return await ctx.send("Operation cancelled.", edit=False)
            else:
                return await ctx.send("Invalid response.", edit=False)
            

    @commands.command()
    async def bal(self, ctx, user: discord.Member = None):
        '''Check how much bananas ya got!'''
        if user:
            ctx.author = user
        bal = await self.balance(ctx)
        level = await self.level(ctx)
        person = "You currently have" if not user else f"**{user.name}** currently has"
        em = discord.Embed(color=0x00ff00, title='Current Balance')
        responses = [
            f"{person} **{bal}** :banana:. Kinda sad. [Level **{level}**]",
            f"Idk how {person} **{bal}** :banana:?! [Level **{level}**]",
            f"REEEEEE! {person} **{bal}** :banana:. [Level **{level}**]",
            f"{person} **{bal}** :banana:. Man, hella rich. [Level **{level}**]",
            f"{person} **{bal}** :banana:. Deal with it. [Level **{level}**]",
            f"{person} **{bal}** :banana:. I wonder where this dood's money comes from?! [Level **{level}**]"
        ]
        em.description = random.choice(responses)
        await ctx.send(embed=em)


    @commands.command(aliases=['daily', 'dailyshit'])
    async def dailycredit(self, ctx):
        '''Collect your daily bananas!'''
        await ctx.trigger_typing()
        time = await self.time_left(ctx)
        if time:
            return await ctx.send(f"This command is on cooldown for: **{time}**.")
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
    @commands.cooldown(1, 60.0, BucketType.user)
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
    @commands.cooldown(1, 300, BucketType.user)
    async def gamble(self, ctx, amount):
        """Choose an amount. Will you win it or will you lose it?"""
        try:
            amount = int(amount)
        except ValueError:
            return await ctx.send("Please enter a valid number for the amount.")
        if amount <= 0:
            return await ctx.send("Gamble more. Not less. Enter a number more than 0.")
        bal = await self.balance(ctx)
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
    @commands.cooldown(1, 180, BucketType.user)
    async def rob(self, ctx, user: discord.Member, points: int):
        """Steal from someone else!"""
        my_points = await self.balance(ctx)
        temp = ctx.author
        ctx.author = user
        target_points = await self.balance(ctx)
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
    @commands.cooldown(1, 120, BucketType.user)
    async def pay(self, ctx, user: discord.Member, points):
        """Donate credits to someone else!"""
        my_points = await self.balance(ctx)    
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
        data = await self.db.economy.find({ "guild": ctx.guild.id }).sort("points", -1).to_list(None)
        em = discord.Embed(title=ctx.guild.name)
        em.set_author(name="Leaderboard", icon_url=ctx.guild.icon_url)
        desc = ""
        count = len(data) if len(data) < 10 else 10
        for i in range(count):
            desc += str(i + 1) + " ❯ " + str(self.bot.get_user(data[i]["user"])) + "\n`" + str(data[i]["points"]) + "` :banana:\n"
        em.description = desc
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Economy(bot))
