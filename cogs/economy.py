import discord
import sys
import os
import io
import json
import ezjson
import random
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Economy:
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def openaccount(self, ctx):
        '''Open an account. Of bananas.'''
        em = discord.Embed(color=discord.Color(value=0x00ff00), title='Open Account')
        f = open("data/economy.json").read()
        x = json.loads(f)
        try:
            x[str(ctx.guild.id)][str(ctx.author.id)]
            em.description = "Looks like you already opened an account on dat banana bot!"
            return await ctx.send(embed=em)
        except KeyError:
            lol = {
                str(ctx.author.id): 0
            }
            ezjson.dump("data/economy.json", ctx.guild.id, lol)
            em.description = "Opened your account. Have fun with bananas!"
            return await ctx.send(embed=em)

        
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
        if x[str(ctx.guild.id)][str(ctx.author.id)]:
            lol = {
                str(ctx.author.id): int(x[str(ctx.guild.id)][str(ctx.author.id)]) + num
            }
            ezjson.dump("data/economy.json", ctx.guild.id, lol)
            return await ctx.send(f"Hooray! Successfully added **{num} :banana: into your account.")
        else:
            return await ctx.send("Oof. You don't have an account yet! Time to create one with `*openaccount`.")
        

    @commands.command()
    async def lottery(self, ctx, numbers: str = None):
        '''Enter the lottery to win/lose! 3 numbers, seperate with commas. Entry is $50, winner gets $10 million!'''
        f = open("data/economy.json").read()
        x = json.loads(f)
        if not x[str(ctx.guild.id)][str(ctx.author.id)]:
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


def setup(bot):
    bot.add_cog(Economy(bot))
