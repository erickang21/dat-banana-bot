import discord
import traceback
import asyncio
from ext.logger import Logger as logger
from discord.ext import commands

class Utils:
    """dat banana bot's custom utility functions for use throughout the code."""
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def clean_text(ctx, text):
        """Removes any mentions from the text."""
        return await commands.clean_content().convert(ctx, text)


    async def handle_exception(self, ctx, error):
        """Handle an uncaught error in general and report to the devs. Should not be called for the most part, since it is used in `on_command_error`."""
        log = self.bot.get_channel(445332002942484482)
        traceback_text = "\n".join(traceback.format_exception(type(error), error, error.__traceback__, 10))
        emb = discord.Embed(color=discord.Color(value=0xf44e42), title="Welp. This is awkward...")
        emb.description = "It shouldn't end this way. :cry:\n\nAn unknown issue has occurred. I have reported the error to the devs, who will check it out. Hang in there!"
        await ctx.send(embed=emb)
        embed = discord.Embed(color=discord.Color(value=0xf44e42), title="Error Report")
        embed.set_author(name=f"{str(ctx.author)} (ID: {ctx.author.id})", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Server", value=ctx.guild.name)
        embed.add_field(name="Server ID", value=ctx.guild.id)
        embed.add_field(name="Channel", value=ctx.channel.name)
        embed.add_field(name="Command Content", value=ctx.message.content)
        embed.description = f"**Full Traceback:**\n\n```{traceback_text}```"
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await log.send(self.bot.get_user(277981712989028353).mention, embed=embed)
        logger.error(error)

    def slice_text(self, text: str, count: int, end="..."):
        """Slices text to a maximum count. Does nothing if text is lower than the count. If more, cuts off and uses the ending given."""
        if len(text) < count:
            return text
        return text[0:count - 3] + end


    async def edit_msg(self, ctx, *msgs, wait_time=3):
        """Loop through all `msgs`. Sends the first message, then edits to all other messages."""
        msgs = list(msgs)
        m = await ctx.send(msgs[0])
        await asyncio.sleep(wait_time)
        msgs.remove(msgs[0])
        for x in msgs:
            await m.edit(content=x)
            await asyncio.sleep(wait_time)

    def get_lines(self, number):
        """Get lines equal to a number."""
        number = int(number)
        if number >= 0 and number <= 10:
            return "||||||||||"
        elif number >= 10 and number <= 20:
            return "**|**||||||||"
        elif number >= 20 and number <= 30:
            return "**||**||||||||"
        elif number >= 30 and number <= 40:
            return "**|||**|||||||"
        elif number >= 40 and number <= 50:
            return "**||||**||||||"
        elif number >= 50 and number <= 60:
            return "**|||||**|||||"
        elif number >= 60 and number <= 70:
            return "**||||||**||||"
        elif number >= 70 and number <= 80:
            return "**|||||||**|||"
        elif number >= 80 and number <= 90:
            return "**||||||||**||"
        elif number >= 90 and number <= 99:
            return "**|||||||||**|"
        elif number == 100:
            return "**||||||||||**"

    @staticmethod
    def format_time(self, time):
        """Format a duration into human-friendly time."""
        time = int(time)
        if time >= 0 and time <= 9:
            return f"0{str(time)}"
        else:
            return time


    def mix(self, word1, word2):
        """Mix two words together."""
        return word1[:int(len(word1) / 2)] + word2[int(len(word2) / 2):]

    def capitalize(self, msg: str):
        res = []
        snakes = msg.split("_")
        for x in snakes:
            res.append(x.title())
        return " ".join(res)
