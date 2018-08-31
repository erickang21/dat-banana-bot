import discord
import sys
import os
import io
import asyncio
import aiohttp
import random
import json
import idioticapi
from discord.ext import commands
import base64
from .utils.utils import Utils

# class Connect4:
#     def __init__(self, bot):
#         self.bot = bot
#         self.ctx = None
#         self.board = [
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False },
#             { "taken": False }
#         ]
#         self.sent = None
#         self.last = 0
#         self.started = False
#         self.winner = False
#         self.tie = False

#     def codify(self, text: str):
#         return "```\n"+text+"```"

#     async def initiate_game(self, ctx: commands.Context):
#         self.ctx = ctx
#         m = self.codify(
#             ""
#         )

class fun:
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.session
        with open('data/apikeys.json') as f:
            lol = json.load(f)
            self.client = lol.get("idioticapi")
        self.giphy_key = lol.get("giphyapi")
        self.cleverbot_user = lol.get("cleverbot_user")
        self.cleverbot_key = lol.get("cleverbot_key")
        self.guess_number = random.randint(1, 100)
        self.utils = Utils(bot)

    def get_lines(self, number):
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

    # @commands.command()
    # async def connect4(self, ctx, user: discord.Member):
    #     """Play connect4 with someone else!"""
    #     await ctx.send(f"Hiya {user.mention}, **{ctx.author.name}** wants to play Connect 4 with you. Reply 'accept' to join or 'decline' to reject (This times out in 30 seconds.)")
    #     x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == user, timeout=30.0)
    #     if x.content.lower() == 'reject':
    #         return await ctx.send(f"Oof, {ctx.author.mention}...Looks like **{user.name}** didn't want to play with you. Oh well.")
    #     elif x.content.lower() == 'accept':


    @commands.command()
    async def weeb(self, ctx):
        """Get a random pic for weebs."""
        resp = await (await self.bot.session.get("https://nekos.life/api/v2/img/avatar")).json()
        em = discord.Embed(color=ctx.author.color, title="Weeb Pic")
        em.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.set_image(url=resp['url'])
        await ctx.send(embed=em)

    @commands.command()
    async def reverse(self, ctx, *, text):
        """!txeT ruoY esreveR"""
        text = await Utils.clean_text(ctx, "".join(list(reversed(str(text)))))
        await ctx.send(text)


    # @commands.command()
    # async def zalgo(self, ctx, *, text):
    #     zalgo_chars = [chr(x) for x in range(768, 879)]
    #     await ctx.send("".join(
    #         c + "".join(
    #             random.choice(zalgo_chars) for _ 
    #             in range(random.randint(2, 7) * c.isalnum()))

    #             for c in text))


    @commands.command()
    async def asktrump(self, ctx, *, question):
        """Ask Trump your own question."""
        resp = await self.bot.session.get(f"https://api.whatdoestrumpthink.com/api/v1/quotes/personalized?q={question}")
        resp = await resp.json()
        em = discord.Embed(color=ctx.author.color, title="What did Trump say?")
        em.description = f"**You:** {question}\n\n**Trump:** {resp['message']}"
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.set_footer(text="Powered by whatdoestrumpthink.com", icon_url="https://d.ibtimes.co.uk/en/full/1571929/donald-trump.jpg")
        await ctx.send(embed=em)

    @commands.command()
    async def meme(self, ctx):
        """Get a random meme. The stuff of life."""
        await ctx.trigger_typing()
        r = await self.bot.session.get("https://api.reddit.com/u/kerdaloo/m/dankmemer/top/.json?sort=top&t=day&limit=500")
        r = await r.json()
        meme = r['data']['children'][random.randint(0, len(r['data']['children']) - 1)]['data']
        meme_img = meme['preview']['images'][0]['source']['url']
        meme_title = meme['title']
        em = discord.Embed(color=discord.Color(value=0x00ff00), title=meme_title)
        em.set_image(url=meme_img)
        em.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)
            

    @commands.command()
    @commands.guild_only()
    async def cleverbot(self, ctx, *, text):
        """Speak to Cleverbot. A chat bot."""
        em = discord.Embed(color=discord.Color(value=0xe5f442), title="Please Wait...")
        em.description = f"{self.bot.get_emoji(452194264953258014)} CleverBot is typing..."
        msg = await ctx.send(embed=em)
        instance_params = {
            "user": self.cleverbot_user,
            "key": self.cleverbot_key,
            "nick": ctx.author.name,
        }
        await self.bot.session.post("https://cleverbot.io/1.0/create", data=instance_params)
        params = {
            "user": self.cleverbot_user,
            "key": self.cleverbot_key,
            "nick": ctx.author.name,
            "text": text
        }
        resp = await self.bot.session.post("https://cleverbot.io/1.0/ask", data=params)
        resp = await resp.json()
        if resp['status'] != "success":
            return await ctx.send(f"An error occurred with Cleverbot.io. More details:\n{resp['status']} ")
        em = discord.Embed(color=ctx.author.color)
        em.set_author(name="CleverBot", icon_url="https://herokuis.a-bad.host/nzJUsqTSY.png")
        em.description = resp['response']
        await msg.edit(embed=em)

        
    @commands.command()
    @commands.guild_only()
    async def rate(self, ctx, Type: str, *, thing):
        """
        Rate someone based on something.
        
        Available commands: 
        *rate gay [user]
        *rate weeb [user]
        """
        try:
            to_rate = ctx.message.mentions[0].name
        except IndexError:
            to_rate = str(thing)
        to_rate = await Utils.clean_text(ctx, to_rate)
        if Type.lower() == 'gay':
            rating = random.randint(0, 100)
            return await ctx.send(f"**{to_rate}**'s gay level: :gay_pride_flag: \n{self.get_lines(rating)} **{rating}%**")
        elif Type.lower() == 'weeb':
            rating = random.randint(0, 100)
            return await ctx.send(f"**{to_rate}**'s weeb level: {self.bot.get_emoji(449682671862546443)}\n{self.get_lines(rating)} **{rating}%**")
        else:
            return await ctx.send("Invalid argument. *rate [gay/weeb] [user]")

    @commands.command()
    async def guess(self, ctx, number):
        """Guess a number between 1 and 1000!"""
        try:
            number = int(number)
        except ValueError:
            return await ctx.send("Please enter a valid number.")
        match = self.guess_number
        if match == number:
            self.guess_number = random.randint(1, 100)
            em = discord.Embed(color=discord.Color(value=0x00ff00))
            em.title = "SUCCESS!"
            em.description = "You guessed the number CORRECT-O! Awesome job."
        else:
            em = discord.Embed(color=discord.Color(value=0xf44542))
            em.title = "Oof..."
            em.description = f"The number was wrong. Keep guessing!"
            await self.bot.get_channel(445332002942484482).send(f"The number is {self.guess_number}")
        return await ctx.send(embed=em)


    @commands.command()
    @commands.guild_only()
    async def ship(self, ctx, one: str, two: str):
        """Who's your true love? Or enemy..."""
        try:
            first = ctx.message.mentions[0].name
        except IndexError:
            first = one
        try:
            second = ctx.message.mentions[1].name
        except IndexError:
            second = two
        #em = discord.Embed(color=discord.Color(value=0xebf442), title='Please wait...')
        #responses = [
        #    "*What's on your mind?*",
        #    "Is she the one?",
        #    "Calculating how much they love each other...",
        #    "Could it be?"
        #]
        #em.description = random.choice(responses)
        #msg = await ctx.send(embed=em)
        #await asyncio.sleep(3)
        rate = random.randint(0, 100)
        if rate < 20:
            text = f"**{first}** + **{second}**\n\nComplete CRAP! :unamused:\n\nRating: **{rate}**%"
        elif rate >= 20 and rate < 40:
            text = f"**{first}** + **{second}**\n\nQuite bad, y'know. {self.bot.get_emoji(430851935864881152)}\n\nRating: **{rate}**%"
        elif rate >= 40 and rate < 60:
            text = f"**{first}** + **{second}**\n\nMeh, it's *okay*, I guess. {self.bot.get_emoji(430851935864881152)}\n\nRating: **{rate}**%"
        elif rate >= 60 and rate < 80:
            text = f"**{first}** + **{second}**\n\nPretty gucci! {self.bot.get_emoji(430851871872253983)}\n\nRating: **{rate}**%"
        elif rate >= 80 and rate <= 100:
            text = f"**{first}** + **{second}**\n\nOne True Pair! {self.bot.get_emoji(430848132667146251)}\n\nRating: **{rate}**%"
        e = discord.Embed(color=discord.Color(value=0x00ff00), title="Matchmaking")
        e.description = text + f"\n\n__Ship Name__\n{self.utils.mix(first, second)}"
        await ctx.send(embed=e)


    
    @commands.command()
    async def emojify(self, ctx, *, text: str):
        """Turns your text into emojis!"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        to_send = ""
        for char in text:
            if char == " ":
                to_send += " "
            elif char.lower() in 'qwertyuiopasdfghjklzxcvbnm':
                to_send += f":regional_indicator_{char.lower()}:  "
            elif char in '1234567890':
                numbers = {
                    "1": "one",
                    "2": "two",
                    "3": "three",
                    "4": "four",
                    "5": "five",
                    "6": "six",
                    "7": "seven",
                    "8": "eight",
                    "9": "nine",
                    "0": "zero"
                }
                to_send += f":{numbers[char]}: "
            else:
                return await ctx.send("Characters must be either a letter or number. Anything else is unsupported.")
        if len(to_send) > 2000:
            return await ctx.send("Emoji is too large to fit in a message!")
        await ctx.send(to_send)
        
    @commands.command(aliases=['re'])
    async def randomemoji(self, ctx):
        """Get a :banana: emote from my :banana: servers"""
        try:
            await ctx.send(str(random.choice([emoji for emoji in ctx.bot.emojis if emoji.require_colons])))
        except ValueError:
            await ctx.send('00F! s0m3thin5 w3nt wr0n5!')
     
    @commands.command()
    @commands.guild_only()
    async def star(self, ctx, *, msg):
        """Git dat star"""
        if (len(msg) > 25):
            return await ctx.send("String must be less than 26 characters")
        elif (len(msg) == 0):
            return await ctx.send("String must be at least 1 character")

        str = '```\n'

        mid = len(msg) - 1

        for i in range(len(msg) * 2 - 1):
            if (mid == i):
                str += msg[::-1] + msg[1:] + "\n"
            else:
                let = abs(mid - i)
                str += " " * (mid - let)
                str += msg[let]
                str += " " * (let - 1)
                str += msg[let]
                str += " " * (let - 1)
                str += msg[let]
                str += "\n"

        str += "```"
        await ctx.send(str)

    @commands.command()
    async def gif(self, ctx):
        """Sends a random GIF, that's memey as hell."""
        try:
            em = discord.Embed(color=discord.Color(value=0x00ff00), title="Random GIF")
            resp = await self.session.get(f'https://api.giphy.com/v1/gifs/trending?api_key={self.giphy_key}') 
            resp = await resp.json()
            em.set_image(url=f"https://media.giphy.com/media/{resp['data'][random.randint(0, len(resp['data']) - 1)]['id']}/giphy.gif")
            em.set_author(name=f"Requested by: {ctx.author.name}", icon_url=ctx.author.avatar_url)
            em.set_footer(text='Powered by Giphy API')
            await ctx.send(embed=em)
        except Exception as e:
            em = discord.Embed(color=discord.Color(value=0xf44242), title="An error occurred.")
            em.description = f"More details: \n\n```{e}```"
            await ctx.send(embed=em)



    @commands.command(aliases=['joke', 'badjoke', 'shitjoke', 'hjoke'])
    async def horriblejoke(self, ctx):
        """It's a REALLY REALLY bad joke. Trust me."""
        resp = await self.session.get('https://08ad1pao69.execute-api.us-east-1.amazonaws.com/dev/random_joke')
        r = await resp.json()
        color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color, title=r['setup'])
        em.description = r['punchline']
        em.set_footer(text="Ha. Ha. Ha. Very funny, huh?")
        await ctx.send(embed=em)

       
       
    @commands.command()
    @commands.guild_only()
    async def hack(self, ctx, user: discord.Member):
        """Hack someone's account! Try it!"""
        text = await Utils.clean_text(ctx, str(user))
        msg = await ctx.send(f"Hacking! Target: {text}")
        await asyncio.sleep(2)
        await msg.edit(content="Accessing Discord Files... [▓▓    ]")
        await asyncio.sleep(2)
        await msg.edit(content="Accessing Discord Files... [▓▓▓   ]")
        await asyncio.sleep(2)
        await msg.edit(content="Accessing Discord Files... [▓▓▓▓▓ ]")
        await asyncio.sleep(2)
        await msg.edit(content="Accessing Discord Files COMPLETE! [▓▓▓▓▓▓]")
        await asyncio.sleep(2)
        await msg.edit(content="Retrieving Login Info... [▓▓▓    ]")
        await asyncio.sleep(3)
        await msg.edit(content="Retrieving Login Info... [▓▓▓▓▓ ]")
        await asyncio.sleep(3)
        await msg.edit(content="Retrieving Login Info... [▓▓▓▓▓▓ ]")
        await asyncio.sleep(4)
        await msg.edit(content=f"An error has occurred hacking {text}'s account. Please try again later. ❌")   
   
    
    @commands.command()
    @commands.guild_only()
    async def roast(self, ctx, user: discord.Member = None):
        '''Roast someone! If you suck at roasting them yourself.'''
        msg = f"Hey, {user.mention}! " if user is not None else ""
        roasts = ["I'd give you a nasty look but you've already got one.", "If you're going to be two-faced, at least make one of them pretty.", "The only way you'll ever get laid is if you crawl up a chicken's ass and wait.", "It looks like your face caught fire and someone tried to put it out with a hammer.", "I'd like to see things from your point of view, but I can't seem to get my head that far up your ass.", "Scientists say the universe is made up of neutrons, protons and electrons. They forgot to mention morons.", "Why is it acceptable for you to be an idiot but not for me to point it out?", "Just because you have one doesn't mean you need to act like one.", "Someday you'll go far... and I hope you stay there.", "Which sexual position produces the ugliest children? Ask your mother.", "No, those pants don't make you look fatter - how could they?", "Save your breath - you'll need it to blow up your date.", "If you really want to know about mistakes, you should ask your parents.", "Whatever kind of look you were going for, you missed.", "Hey, you have something on your chin... no, the 3rd one down.", "I don't know what makes you so stupid, but it really works.", "You are proof that evolution can go in reverse.", "Brains aren't everything. In your case they're nothing.", "I thought of you today. It reminded me to take the garbage out.", "You're so ugly when you look in the mirror, your reflection looks away.", "Quick - check your face! I just found your nose in my business.", "It's better to let someone think you're stupid than open your mouth and prove it.", "You're such a beautiful, intelligent, wonderful person. Oh I'm sorry, I thought we were having a lying competition.", "I'd slap you but I don't want to make your face look any better.", "You have the right to remain silent because whatever you say will probably be stupid anyway."]
        await ctx.send(f"{msg} {random.choice(roasts)}")


    @commands.command()
    async def yomomma(self, ctx):
        '''Sends a random yo momma joke. Outdated?'''
        resp = await self.session.get("http://api.yomomma.info/") 
        resp = await resp.json(content_type=None)
        await ctx.send(resp['joke'])




    # @commands.command(aliases=['animation', 'a'])
    # async def anim(self, ctx, Type):
    #     """Animations! Usage: *anim [type]. For a list, use *anim list."""
    #     if Type is None:
    #         await ctx.send('Probably a really cool animation, but we have not added them yet! But hang in there! You never know... For a current list, type *anim list')
    #     else:
    #         if Type.lower() == 'wtf':
    #             msg = await ctx.send("```W```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```WO```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```WOT```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```WOT D```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```WOT DA```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```WOT DA F```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```WOT DA FU```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```WOT DA FUK```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```WOT DA FUK!```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="WOT DA FUK!")
    #         elif Type.lower() == 'mom':
    #             msg = await ctx.send("```Y```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```YO```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```YO M```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```YO MO```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```YO MOM```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```YO MOM!```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="YO MOM!")
    #         elif Type.lower() == 'gethelp':
    #             msg = await ctx.send("```STOP!```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```STOP! G```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```STOP! Ge```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```STOP! Get```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```STOP! Get s```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```STOP! Get so```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```STOP! Get som```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```STOP! Get some```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```STOP! Get some HELP```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```STOP! Get some HELP!!!```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="STOP! Get some HELP!!!")
    #         elif Type.lower() == 'sike':
    #             msg = await ctx.send("```W```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Wa```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Wai```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Wait```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Wait.```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Wait..```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Wait...```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```SIKE!```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="SIKE!")
    #         elif Type.lower() == 'gitgud':
    #             msg = await ctx.send("```G```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Gi```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Git```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Git GUD!```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="Git GUD!")
    #         elif Type.lower() == 'clock':
    #             msg = await ctx.send(":clock12:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock1230:") 
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock1:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock130:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock2:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock230:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock3:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock330:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock4:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock430:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock5:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock530:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock6:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock630:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock7:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock730:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock8:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock830:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock9:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock930:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock10:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock1030:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock11:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock1130:")
    #             await asyncio.sleep(1)
    #             await msg.edit(content=":clock12:")
    #         elif Type.lower() == 'mate':
    #             msg = await ctx.send("```Y```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Ye```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Ye W```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Ye WO```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Ye WOT```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Ye WOT M8```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Ye WOT M8?!?!?!")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="Ye WOT M8?!?!?!")
    #         elif Type.lower() == 'oj':
    #             msg = await ctx.send("```M```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Mm```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Mmm```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Mmm i```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Mmm it```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Mmm it'```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Mmm it's```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Mmm it's a```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Mmm it's a ORANGE```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="```Mmm it's a ORANGE JUICE```")
    #             await asyncio.sleep(1)
    #             await msg.edit(content="Mmm it's a ORANGE JUICE")             
    #         elif Type.lower() == 'list':
    #             color = discord.Color(value=0x00ff00)
    #             em=discord.Embed(color=color, title="Current List of Awesome Animations:")
    #             em.description = "wtf (anim wtf), mom (anim mom), gethelp (anim gethelp), sike (anim sike), gitgud (anim gitgud), clock (anim clock), mate (anim mate), oj (anim oj)."
    #             em.set_footer(text="We will always be adding new animations!")
    #             await ctx.send(embed=em)
    #         else:
    #             await ctx.send('Probably a really cool animation, but we have not added them yet! But hang in there! You never know... For a current list, type *anim list')             
              
   
    @commands.command()
    async def eightball(self, ctx, *, message:str):
        """Really desperate? Ask the 8ball for advice. Only yes/no questions!"""
        choices = ['It is certain. :white_check_mark:', 'It is decidedly so. :white_check_mark:', 'Without a doubt. :white_check_mark:', 'Yes, definitely. :white_check_mark:', 'You may rely on it. :white_check_mark:', 'As I see it, yes. :white_check_mark:', 'Most likely. :white_check_mark:', ' Outlook good. :white_check_mark:', 'Yes. :white_check_mark:', 'Signs point to yes. :white_check_mark:', 'Reply hazy, try again. :large_orange_diamond: ', 'Ask again later. :large_orange_diamond: ', 'Better not tell you now. :large_orange_diamond: ', 'Cannot predict now. :large_orange_diamond: ', 'Concentrate and ask again. :large_orange_diamond: ', 'Do not count on it. :x:', 'My reply is no. :x:', 'My sources say no. :x:', 'Outlook not so good. :x:', 'Very doubtful. :x:']
        color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color, title=f"{message}")
        em.description = random.choice(choices) 
        em.set_author(name="The Mighty 8 ball", icon_url="https://vignette.wikia.nocookie.net/battlefordreamislandfanfiction/images/5/53/8-ball_my_friend.png/revision/latest?cb=20161109021012")
        em.set_footer(text=f"Sent by {ctx.message.author.name}")
        await ctx.message.delete()
        await ctx.send(embed=em)
        
        
    @commands.group(invoke_without_command=True)
    async def base64(self, ctx):
        '''Encode and decode base64 Text time to annoy your friends with encoded text.'''
        await ctx.send("Base64 Encode/Decode\nCommands: encode: Encode text\ndecode: Decode text")

    @base64.command()
    async def encode(self, ctx, *, msg: str):
        '''Encode base64 text'''
        try:
            x = base64.b64encode(msg.encode("ascii")).decode("ascii")
            if len(x) > 1950: return await ctx.send("Results too long.")
            res = await Utils.clean_text(ctx, x)
            await ctx.send(f"```{res}```") 
        except Exception as e:
            await ctx.send("Something went wrong.")
            print(e)
        
    @base64.command()
    async def decode(self, ctx, *, msg: str):
        '''Decode base64 text'''
        try:
            x = base64.b64decode(msg)
            if len(x) > 1950: return await ctx.send("Results too long.")
            res = await Utils.clean_text(ctx, x.decode('ascii'))
            await ctx.send(f"```{res}```")
        except Exception as e:
            await ctx.send("Invalid Base64 Text")
            print(e)

def setup(bot):
    bot.add_cog(fun(bot))
