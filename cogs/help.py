import discord
import sys
import os
import io
import asyncio
import aiohttp
import textwrap
from discord.ext import commands
from .utils.paginator import HelpPaginator, CannotPaginate
from .utils.datpaginator import DatPaginator


class Help:
    def __init__(self, bot):
       self.bot = bot

    
    @commands.command(name='help')
    async def _help(self, ctx, *, command: str = None):
        """Shows help about a command or the bot"""
        
        try:
            if command is None:
                p = await HelpPaginator.from_bot(ctx)
            else:
                entity = self.bot.get_cog(command) or self.bot.get_command(command)

                if entity is None:
                    clean = command.replace('@', '@\u200b')
                    return await ctx.send(f'Command or category "{clean}" not found.')
                elif isinstance(entity, commands.Command):
                    p = await HelpPaginator.from_command(ctx, entity)
                else:
                    p = await HelpPaginator.from_cog(ctx, entity)

            await p.paginate()
        except Exception as e:
            await ctx.send(e)
            
    @commands.command()
    async def testhelp(self, ctx, *, command: str = None):
        """HELP! Not this one, tho..."""
        try:
            if command is None:
                color = discord.Color(value=0x00ff00)
                em = discord.Embed(color=color, title='dat banana bot Help')
                lol = []
                commands = []
                pgnumber = 0
                for x in self.bot.cogs:
                    lol.append(x)
                for x in lol:
                    cmdlist = self.bot.get_cog_commands(x)
                    if x == lol[pgnumber]:
                        commands.append(cmdlist)
                for x in commands:
                    em.description += f"**{x.callback.__name__}**\n{x.short_doc}"
            em.set_footer(
                text="Pulling your hair out? Use the '?' to GET HELP!")
            msg = await ctx.send(embed=em)
            try:
                await msg.add_reaction("\U000021a9")  # Fast forward left
                await msg.add_reaction("\U00002b05")  # Turn left
                await msg.add_reaction("\U000027a1")  # Turn right
                await msg.add_reaction("\U000021aa")  # Fast forward right
                await msg.add_reaction("\U0001f6d1")  # Stop
                await msg.add_reaction("\U00002049")  # Info
            except discord.Forbidden:
                return await ctx.send("Uh-oh! I don't have the 'Add Reactions' permission, so I can't paginate...")
            while True:
                reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction: x.channel == ctx.channel and x.author == ctx.author and user == ctx.author, timeout=120.0)
                if reaction.emoji == '⬅':
                    try:
                        await msg.remove_reaction("\U00002b05", ctx.author)
                    except:
                        pass
                    pgnumber -= 1
                    em.description = ''
                    for x in commands:
                        em.description += f"**{x.name}**\n{x.short_doc}"
                    await msg.edit(embed=em)
                elif reaction.emoji == '➡':
                    try:
                        await msg.remove_reaction("\U000027a1", ctx.author)
                    except:
                        pass
                    pgnumber += 1
                    em.description = ''
                    for x in commands:
                        em.description += f"**{x.name}**\n{x.short_doc}"
                    await msg.edit(embed=em)
                elif reaction.emoji == 'ℹ':
                    try:
                        await msg.remove_reaction("\U00002139", ctx.author)
                    except:
                        pass
                    em.description = textwrap.dedent("""
                    **What do these buttons do?**
                    
                    :arrow_left: Turns left one page.
                    :arrow_right: Turns right one page.
                    :information_source: Shows this message.
                    """)
                    em.set_footer(text="This will revert back in 15 seconds.")
                    await msg.edit(embed=em)
                    await asyncio.sleep(15)
                    await msg.edit(embed=msg)
                elif reaction.emoji == '⏹':
                    await msg.delete()
                    break
        except Exception as e:
           await ctx.send(f"An error occured. More details: \n\n```{e}```")



    @commands.command()
    async def paginate(self, ctx):
        p = DatPaginator(ctx, ["Page 1", "Page 2", "Page 3","Page 4", "Page 5"], page_count=True)
        await p.run()






def setup(bot): 
    bot.add_cog(Help(bot))   
