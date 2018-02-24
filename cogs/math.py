import discord
import sys
import os
import io
import asyncio
from discord.ext import commands


class Math:
    def __init__(self, bot):
       self.bot = bot
                
    
                                              
    @commands.command()
    async def add(self, ctx, num: int, num2: int):
        '''ADD EM UP! Yep.'''
        if num is None:
            await ctx.send("Aren't you stupid enough? Usage: *add [no.1] [no.2]")
        else:
            await ctx.send(num + num2)
                
                
    @commands.command()
    async def subtract(self, ctx, num: int, num2: int):
        '''That big MINUS. Usage: *subtract [no.1] [no.2]'''
        if num is None:
            await ctx.send("Aren't you stupid enough? Usage: *subtract [no.1] [no.2]")
        else:
            await ctx.send(num - num2)
                
                
    @commands.command()
    async def multiply(self, ctx, num: int, num2: int):
        '''Multiply em. Git ready! Usage: *multiply [no.1] [no.2]'''
        if num is None:
            await ctx.send("Aren't you stupid enough? Usage: *multiply [no.1] [no.2]")
        else:
            await ctx.send(num * num2)
                
                
    @commands.command()
    async def divide(self, ctx, num: int, num2: int):
        '''Divide em. Cut em. Idc. Usage: *multiply [no.1] [no.2]'''
        if num is None:
            await ctx.send("Aren't you stupid enough? Usage: *divide [no.1] [no.2]")
        else:
            await ctx.send(num / num2)


    @commands.command()
    async def calc(self, ctx, num1=None, sign=None, num2=None):
        '''Does some simple math for you.'''
        if num1 is None:
            await ctx.send("You are missing a number. Missing Arg: num1")
        if num2 is None:
            await ctx.send("You are missing a number. Missing Arg: num2")
        if sign is None:
            await ctx.send("Please enter a sign. +, -, x, /. Missing Arg: sign \nExample: *calc 3 + 4")
        else:
            try:
                float(num1)
                float(num2)
            except ValueError:
                await ctx.send("One of your numbers ain't a number! Enter your formula like this: *calc [number] [+|-|x|/] [number] \nExample: *calc 3 + 4")
            else:
                num1 = float(num1)
                num2 = float(num2)
                if sign == '+':
                    color = discord.Color(value=0x00ff00)
                    em = discord.Embed(color=color, title='Calculator')
                    em.add_field(name='Input:', value=f'{num1}+{num2}')
                    em.add_field(name='Output:', value=f'{num1 + num2}')
                    await ctx.send(embed=em)
                if sign == '-':
                    color = discord.Color(value=0x00ff00)
                    em = discord.Embed(color=color, title='Calculator')
                    em.add_field(name='Input:', value=f'{num1}-{num2}')
                    em.add_field(name='Output:', value=f'{num1 - num2}')
                    await ctx.send(embed=em)
                if sign == 'x':
                    color = discord.Color(value=0x00ff00)
                    em = discord.Embed(color=color, title='Calculator')
                    em.add_field(name='Input:', value=f'{num1}x{num2}')
                    em.add_field(name='Output:', value=f'{num1 * num2}')
                    await ctx.send(embed=em)
                if sign == '/':
                    color = discord.Color(value=0x00ff00)
                    em = discord.Embed(color=color, title='Calculator')
                    em.add_field(name='Input:', value=f'{num1}+{num2}')
                    em.add_field(name='Output:', value=f'{num1 / num2}')
                    await ctx.send(embed=em)
                else:
                    await ctx.send("Please enter a valid sign: +, -, x, / \n Example: *calc 3 + 4")


def setup(bot): 
    bot.add_cog(Math(bot))  
