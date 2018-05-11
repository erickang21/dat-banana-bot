import discord
import sys
import os
import io
import json
import ezjson
import random
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Error(Exception):
    pass


class Economy:
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.session
        self.db = self.bot.db
        with open('data/apikeys.json') as f:
            x = json.loads(f.read())
        self.dbl = x['dblapi']

    async def add_points(self, user, points):
        x = await self.db.economy.find_one({"user": user.id})
        total = int(x['points']) + points
        await self.db.economy.update_one({"user": user.id}, {"$set": {"points": int(total)}}, upsert=True)
        

    async def is_registered(self, user):
        x = await self.db.economy.find_one({"user": user.id})
        if x is None:
            return False
        else:
            return True


    @commands.command(aliases=['register', 'openbank'])
    async def openaccount(self, ctx):
        '''Opens a bank account for the economy!'''
        registered = await self.is_registered(ctx.author)
        if registered:
            return await ctx.send(f"You already have a bank account!")
        await self.db.economy.update_one({"user": ctx.author.id}, {"$set": {"points": 0}}, upsert=True)
        await ctx.send("Your bank account is now open! GLHF!")


        
    @commands.command(aliases=['bal'])
    async def balance(self, ctx, user: discord.Member = None):
        '''Check how much bananas ya got!'''
        person = "You currently have" if not user else f"**{user.name}** currently has"
        user = user or ctx.author
        em = discord.Embed(color=discord.Color(value=0x00ff00), title='Current Balance')
        x = await self.db.economy.find_one({"user": user.id})
        if not x:
            em.description = f"{person} don't have an account on dat banana bot yet! Open one using `*openaccount`."
        else:
            em.description = f"{person} **{x['points']}** :banana:. WOOP!"
        await ctx.send(embed=em)


    @commands.command(aliases=['daily', 'dailyshit'])
    @commands.cooldown(1, 86400.0, BucketType.user)
    async def dailycredit(self, ctx):
        '''Collect your daily bananas!'''
        # async with self.session.get(f"https://discordbots.org/api/bots/388476336777461770/check?userId={ctx.author.id}", headers={'Authorization': self.dbl}) as resp:
        #     resp = await resp.json()
        #     if resp['voted'] == 0:
        #         em = discord.Embed(color=discord.Color(value=0x00ff00), title='Did you vote for dat banana bot today?')
        #         em.description = "You can get an extra **500** points from daily credit by simply upvoting dat banana bot. Click [here](https://discordbots.org/bot/388476336777461770/vote) to vote now.\n\nReact with :white_check_mark: to go upvote, or :x: to receive the reduced daily credit."
        #         msg = await ctx.send(embed=em)
        #         await msg.add_reaction("\U00002705")
        #         await msg.add_reaction("\U0000274c")
        #         reaction, user = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author)
        #         if reaction.emoji == '✅':
        #             return await ctx.send("Thank you! The link (for your convenience) is: https://discordbots.org/bot/388476336777461770/vote")
        #         elif reaction.emoji == '❌':
        #             number = random.randint(100, 300)
        #             try:
        #                 await self.add_points(ctx.author, number)
        #             except Exception as e:
        #                 return await ctx.send(f"Aw, shucks! An unexpected error occurred: \n```{e}```")
        #             return await ctx.send(f"Hooray! Successfully added **{number}** :banana: into your account.")
        #     else:
        x = await self.db.economy.find_one({"user": ctx.author.id})
        if not x:
            return await ctx.send("You don't have an account on dat banana bot yet! Time to open one with `*openaccount.`")
        number = random.randint(300, 500)
        try:
            await self.add_points(ctx.author, number)
        except Exception as e:
            return await ctx.send(f"Aw, shucks! An unexpected error occurred: \n```{e}```")
        return await ctx.send(f"Hooray! Successfully added **{number}** :banana: into your account.")
        

        

    @commands.command()
    async def lottery(self, ctx, numbers: str = None):
        '''Enter the lottery to win/lose! 3 numbers, seperate with commas. Entry is $50, winner gets $10 million!'''
        x = await self.db.economy.find_one({"user": ctx.author.id})
        if x is None:
            return await ctx.send("Oof. You don't have an account yet! Time to create one with `*openaccount`.")
        if int(x['points']) < 100:
            return await ctx.send("Entering the lottery requires 100 :banana:. You don't have enough! Keep on earning 'em")
        if numbers is None:
            return await ctx.send("Please enter 3 numbers seperated by commas to guess the lottery! \nExample: *lottery 1,2,3")
        numbers = numbers.replace(' ', '')
        numbers = numbers.split(',')
        lucky = [str(random.randint(0, 9)), str(random.randint(0, 9)), str(random.randint(0, 9))]
        for i in numbers:
            try:
                int(i)
            except ValueError:
                return await ctx.send("Please enter only numbers for the lottery!")
        lol = ""
        for x in lucky:
            lol += f"`{x}` "
        if numbers == lucky:
            await self.add_points(ctx.author, 10000000)
            em = discord.Embed(color=discord.Color(value=0x00ff00), title='You are the lucky winner!')
            em.description = 'Awesome job! You are part of the 0.8% population that won the lottery! :tada:\n\nYou won 10,000,000 :banana:!'
            return await ctx.send(embed=em)
        else:
            await self.add_points(ctx.author, -100)
            em = discord.Embed(color=discord.Color(value=0xf44e42))
            em.description = f"Ouch. You are part of the 99.2% population that didn't cut it! ¯\_(ツ)_/¯\n\nThe winning numbers were: \n{lol}\n\nYou lost: 100 :banana:"
            return await ctx.send(embed=em)


    @commands.command(aliases=['bet'])
    async def gamble(self, ctx, amount):
        """Choose an amount. Will you win it or will you lose it?"""
        x = await self.db.economy.find_one({"user": ctx.author.id})
        if not x:
            return await ctx.send("You haven't created an account on dat banana bot yet! Time to create one with `*openaccount`")
        try:
            amount = int(amount)
        except ValueError:
            return await ctx.send("Please enter a valid number for the amount.")
        if amount > x['points']:
            return await ctx.send(f"You gambled WAY TOO MUCH! You currently can gamble up to **{x['points']}** :banana:.")
        choose = random.randint(1, 2)
        if choose == 1:
            await self.add_points(ctx.author, amount)
            return await ctx.send(f"HOORAY! You won **{amount}** :banana:. YEET!")
        elif choose == 2:
            await self.add_points(ctx.author, -amount)
            return await ctx.send(f"Aw, man! You just lost **{amount}** :banana:. Better luck next time!")


    @commands.command(aliases=['give'])
    @commands.has_permissions(manage_guild=True)
    async def reward(self, ctx, user: discord.Member, points):
        '''Reward a good person'''
        if not self.is_registered(user):
            return await ctx.send(f"ACK! **{str(user)}** doesn't have an account yet, so they can't get the gucci money!")
        else:
            try:
                points = int(points)
            except ValueError:
                return await ctx.send("ACK! Please enter a valid number for points.")
            try:
                await self.add_points(user, points)
                await ctx.send(f"YEET! Added **{points}** :banana: to **{str(user)}**!")
            except Exception as e:
                await ctx.send(f"Oops, something went wrong. ```{e}```Please report to the developers!")
                print(e)

    @commands.command(aliases=['remove'])
    @commands.has_permissions(manage_guild=True)
    async def deduct(self, ctx, user: discord.Member, points):
        '''Fines a bad boi.'''
        if not self.is_registered(user):
            return await ctx.send(f"ACK! **{str(user)}** doesn't have an account yet, so you can't take away money from them!")
        else:
            try:
                points = int(points)
            except ValueError:
                return await ctx.send("ACK! Please enter a valid number for points.")
            try:
                await self.add_points(user, -points)
                await ctx.send(f"OOF! Removed **{points}** :banana: to **{str(user)}**!")
            except Exception as e:
                await ctx.send(f"Oops, something went wrong. ```{e}```Please report to the developers!")
                print(e)


def setup(bot):
    bot.add_cog(Economy(bot))
