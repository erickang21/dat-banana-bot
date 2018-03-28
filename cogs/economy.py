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

    def add_points(self, id, points):
        f = json.loads(open("data/economy.json").read())
        try:
            points = int(points)
        except ValueError:
            raise Error("Points must be a number or atleast possible to be converted to a number")
        f[str(id)] += int(points)
        x = open("data/economy.json", "w")
        x.write(json.dumps(f, indent=4))
        x.close()

    def is_registered(self, id):
        f = json.loads(open("data/economy.json").read())
        try:
            if f.get(str(id), None) >= 0:
                return True
        except TypeError:  # best i could think of, maybe
            return False


    @commands.command(aliases=['register', 'bank', 'openbank'])
    async def openaccount(self, ctx):
        '''Opens a bank account for the economy!'''
        f = json.loads(open("data/economy.json").read())
        if self.is_registered(ctx.author.id):
            return await ctx.send(f"You already have a bank account, current balance: {f[str(ctx.author.id)]}")
        f[ctx.author.id] = 0
        try:
            x = open("data/economy.json", "w")
            x.write(json.dumps(f, indent=4))
            x.close() 
            await ctx.send("Opened a bank account, have fun!")
        except Exception as e:
            await ctx.send(f"Oh no something went wrong: ```{e}```Please report to the developers")
            print(e)

        
    @commands.command()
    async def balance(self, ctx):
        '''Check how much bananas ya got!'''
        em = discord.Embed(color=discord.Color(value=0x00ff00), title='Current Balance')
        f = open("data/economy.json").read()
        x = json.loads(f)
        try:
            em.description = f"You currently have {x[str(ctx.guild.id)][str(ctx.author.id)]} :banana:."
        except KeyError:
            em.description = "You don't have an account on dat banana bot yet! Open one using `*openaccount`."
        await ctx.send(embed=em)


    @commands.command()
    @commands.cooldown(1, 86400.0, BucketType.user)
    async def dailycredit(self, ctx):
        '''Collect your daily bananas!'''
        num = random.randint(100, 200)
        f = open("data/economy.json").read()
        x = json.loads(f)
        try:
            x[str(ctx.guild.id)][str(ctx.author.id)]
        except KeyError:
            return await ctx.send("Oof. You don't have an account yet! Time to create one with `*openaccount`.")
        lol = {
            str(ctx.author.id): int(x[str(ctx.guild.id)][str(ctx.author.id)]) + num
        }
        ezjson.dump("data/economy.json", ctx.guild.id, lol)
        return await ctx.send(f"Hooray! Successfully added **{num}** :banana: into your account.")

        

    @commands.command()
    async def lottery(self, ctx, numbers: str = None):
        '''Enter the lottery to win/lose! 3 numbers, seperate with commas. Entry is $50, winner gets $10 million!'''
        f = open("data/economy.json").read()
        x = json.loads(f)
        try:
            x[str(ctx.guild.id)][str(ctx.author.id)]
        except KeyError:
            return await ctx.send("Oof. You don't have an account yet! Time to create one with `*openaccount`.")
        if int(x[str(ctx.guild.id)][str(ctx.author.id)]) < 100:
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
            lol = {
                str(ctx.author.id): x[str(ctx.guild.id)][str(ctx.author.id)] + 10000000
            }
            ezjson.dump("data/economy.json", ctx.guild.id, lol)
            em = discord.Embed(color=discord.Color(value=0x00ff00), title='You are the lucky winner!')
            em.description = 'Awesome job! You are part of the 0.8% population that won the lottery! :tada:\n\nYou won 10,000,000 :banana:!'
            return await ctx.send(embed=em)
        else:
            lol = {
                str(ctx.author.id): x[str(ctx.guild.id)][str(ctx.author.id)] - 100
            }
            ezjson.dump("data/economy.json", ctx.guild.id, lol)
            em = discord.Embed(color=discord.Color(value=0xf44e42))
            em.description = f"Ouch. You are part of the 99.2% population that didn't cut it! ¯\_(ツ)_/¯\n\nThe winning numbers were: \n{lol}\n\nYou lost: 100 :banana:"
            return await ctx.send(embed=em)

    @commands.command(aliases=['give'])
    @commands.has_permissions(manage_guild=True)
    async def reward(self, ctx, user: discord.Member, points: int):
        '''Reward a good person'''
        if not self.is_registered(user.id):
            return await ctx.send("Sorry, the user doesn't have a bank account, tell them to `*openaccount` and try again")
        else:
            try:
                self.add_points(user.id, points)
                await ctx.send(f"Added {points} to {user.name}!")
            except Exception as e:
                await ctx.send(f"Oops something went wrong. ```{e}```Please report to the developers")
                print(e)


def setup(bot):
    bot.add_cog(Economy(bot))
