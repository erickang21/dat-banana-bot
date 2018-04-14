import discord
import os
import io
import idioticapi
import random
import json
from discord.ext import commands



class Idiotic:
    def __init__(self, bot):
        self.bot = bot
        with open('data/apikeys.json') as f:
            lol = json.load(f)
        self.client = lol.get("idioticapi")

    def format_avatar(self, avatar_url):
        if avatar_url.endswith(".gif"):
            return avatar_url + "?size=2048"
        return avatar_url.replace("webp", "png")


    @commands.command(aliases=['triggered'])
    async def triggeredpic(self, ctx, user: discord.Member = None):
        """TRI GER RED!!!"""
        if user is None:
            user = ctx.author
        try:
            await ctx.trigger_typing()
            client = idioticapi.Client(self.client, dev=True)
            av = self.format_avatar(user.avatar_url)
            await ctx.send(f"Grrrr...**{user.name}** is triggered.", file=discord.File(await client.triggered(av), "triggered.gif"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def batslap(self, ctx, user: discord.Member = None):
        """User 1 will be slapping, user 2 will BE SLAPPED! Tehehe!"""
        if user is None:
            await ctx.send("Gotta tag someone that you wanna slap!")
        else:
            await ctx.trigger_typing()
            try:
                client = idioticapi.Client(self.client, dev=True)
                av = self.format_avatar(user.avatar_url)
                avatar = self.format_avatar(ctx.author.avatar_url)
                await ctx.send(f"Ouch! **{ctx.author.name}** slapped **{user.name}!**", file=discord.File(await client.batslap(avatar, av), "batslap.png"))
            except Exception as e:
                await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")


    @commands.command()
    async def missing(self, ctx, user: discord.Member = None):
        """Uh-oh...someone went missing!"""
        await ctx.trigger_typing()
        user = ctx.author if user is None else user
        try:
            client = idioticapi.Client(self.client, dev=True)
            await ctx.send(f"**{user.name}** went missing!", file=discord.File(await client.missing(user.avatar_url, user.name), "missing.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")


    @commands.command()
    async def wanted(self, ctx, user: discord.Member = None):
        """Someone is WANTED!"""
        await ctx.trigger_typing()
        user = ctx.author if user is None else user
        try:
            client = idioticapi.Client(self.client, dev=True)
            await ctx.send(f"**{user.name}** is wanted!", file=discord.File(await client.wanted(user.avatar_url), "wanted.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")


    @commands.command()
    async def achievement(self, ctx, *, text=None):
        """Give yourself an achievement. You need one."""
        text = text if text else "Not putting text when using this command."
        try:
            client = idioticapi.Client(self.client, dev=True)
            await ctx.send(f"**{ctx.author.name}** got an achievement!", file=discord.File(await client.achievement(ctx.author.avatar_url, text), "achievement.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")


    @commands.command()
    async def facepalm(self, ctx, user: discord.Member = None):
        user = user if user is not None else ctx.author
        try:
            client = idioticapi.Client(self.client, dev=True)
            await ctx.send(f"**{user.name}** had to facepalm.", file=discord.File(await client.facepalm(user.avatar_url), "facepalm.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def beautiful(self, ctx, user: discord.Member = None):
        user = user if user is not None else ctx.author
        try:
            client = idioticapi.Client(self.client, dev=True)
            await ctx.send(f"**{user.name}** is beautiful!", file=discord.File(await client.beautiful(user.avatar_url), "beautiful.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def stepped(self, ctx, user: discord.Member = None):
        user = user if user is not None else ctx.author
        try:
            client = idioticapi.Client(self.client, dev=True)
            await ctx.send(f"**{user.name}** got stepped on.", file=discord.File(await client.stepped(user.avatar_url), "stepped.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

    @commands.command()
    async def fear(self, ctx, user: discord.Member = None):
        user = user if user is not None else ctx.author
        try:
            client = idioticapi.Client(self.client, dev=True)
            await ctx.send(f"**{user.name}** is SCARY!", file=discord.File(await client.heavyfear(user.avatar_url), "fear.png"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")


def setup(bot):
    bot.add_cog(Idiotic(bot))
