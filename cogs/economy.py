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
        x = await self.db.datbananabot.economy.find_one({"user": user.id})
        total = int(x['points']) + points
        await self.db.datbananabot.economy.update_one({"user": user.id}, {"$set": {"points": total}}, upsert=True)
        

    async def is_registered(self, user):
        x = await self.db.datbananabot.economy.find_one({"user": user.id})
        if x is None:
            return False
        else:
            return True


    @commands.command(aliases=['register', 'openbank'])
    async def openaccount(self, ctx):
        '''Opens a bank account for the economy!'''
        registered = await self.is_registered(ctx.author)
        if registered is True:
            return await ctx.send(f"You already have a bank account!")
        await self.db.datbananabot.economy.update_one({"user": ctx.author.id}, {"$set": {"points": 0}}, upsert=True)
        await ctx.send("Your bank account is now open! GLHF!")


        
    @commands.command()
    async def balance(self, ctx):
        '''Check how much bananas ya got!'''
        em = discord.Embed(color=discord.Color(value=0x00ff00), title='Current Balance')
        x = await self.db.datbananabot.economy.find_one({"user": ctx.author.id})
        try:
            em.description = f"You currently have **{x['points']}** :banana:. WOOP!"
        except KeyError:
            em.description = "You don't have an account on dat banana bot yet! Open one using `*openaccount`."
        await ctx.send(embed=em)


    @commands.command()
#    @commands.cooldown(1, 86400.0, BucketType.user)
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
        number = random.randint(600, 800)
        try:
            await self.add_points(ctx.author, number)
        except Exception as e:
            return await ctx.send(f"Aw, shucks! An unexpected error occurred: \n```{e}```")
        return await ctx.send(f"Hooray! Successfully added **{number}** :banana: into your account.")
        

        

    # @commands.command()
    # async def lottery(self, ctx, numbers: str = None):
    #     '''Enter the lottery to win/lose! 3 numbers, seperate with commas. Entry is $50, winner gets $10 million!'''
    #     x = await self.db.datbananabot.economy.find_one({"id": ctx.guild.id}, {"user": ctx.author.id})
    #     try:
    #         x['user']['points']
    #     except KeyError:
    #         return await ctx.send("Oof. You don't have an account yet! Time to create one with `*openaccount`.")
    #     if int(x['user']['points']) < 100:
    #         return await ctx.send("Entering the lottery requires 100 :banana:. You don't have enough! Keep on earning 'em")
    #     if numbers is None:
    #         return await ctx.send("Please enter 3 numbers seperated by commas to guess the lottery! \nExample: *lottery 1,2,3")
    #     numbers = numbers.replace(' ', '')
    #     numbers = numbers.split(',')
    #     lucky = [str(random.randint(0, 9)), str(random.randint(0, 9)), str(random.randint(0, 9))]
    #     for i in numbers:
    #         try:
    #             int(i)
    #         except ValueError:
    #             return await ctx.send("Please enter only numbers for the lottery!")
    #     lol = ""
    #     for x in lucky:
    #         lol += f"`{x}` "
    #     if numbers == lucky:
    #         lol = {
    #             str(ctx.author.id): x[str(ctx.guild.id)][str(ctx.author.id)] + 10000000
    #         }
    #         ezjson.dump("data/economy.json", ctx.guild.id, lol)
    #         em = discord.Embed(color=discord.Color(value=0x00ff00), title='You are the lucky winner!')
    #         em.description = 'Awesome job! You are part of the 0.8% population that won the lottery! :tada:\n\nYou won 10,000,000 :banana:!'
    #         return await ctx.send(embed=em)
    #     else:
    #         lol = {
    #             str(ctx.author.id): x[str(ctx.guild.id)][str(ctx.author.id)] - 100
    #         }
    #         ezjson.dump("data/economy.json", ctx.guild.id, lol)
    #         em = discord.Embed(color=discord.Color(value=0xf44e42))
    #         em.description = f"Ouch. You are part of the 99.2% population that didn't cut it! ¯\_(ツ)_/¯\n\nThe winning numbers were: \n{lol}\n\nYou lost: 100 :banana:"
    #         return await ctx.send(embed=em)

    # @commands.command(aliases=['give'])
    # @commands.has_permissions(manage_guild=True)
    # async def reward(self, ctx, user: discord.Member, points: int):
    #     '''Reward a good person'''
    #     if not self.is_registered(user.id):
    #         return await ctx.send("Sorry, the user doesn't have a bank account, tell them to `*openaccount` and try again")
    #     else:
    #         try:
    #             self.add_points(user.id, points)
    #             await ctx.send(f"Added {points} to {user.name}!")
    #         except Exception as e:
    #             await ctx.send(f"Oops something went wrong. ```{e}```Please report to the developers")
    #             print(e)


def setup(bot):
    bot.add_cog(Economy(bot))
