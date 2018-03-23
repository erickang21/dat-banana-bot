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


class fun:
    def __init__(self, bot):
        self.bot = bot
        with open('data/apikeys.json') as f:
            lol = json.load(f)
            self.client = lol.get("idioticapi")


    def format_avatar(self, avatar_url):
        if avatar_url.endswith(".gif"):
            return avatar_url + "?size=2048"
        return avatar_url.replace("webp","png")


    @commands.command()
    async def lottery(self, ctx, numbers: str = None):
        '''Enter the lottery to win/lose! 3 numbers, seperate with commas.'''
        if numbers is None:
            return await ctx.send("Please enter 3 numbers seperated by commas to guess the lottery! \nExample: *lottery 1,2,3")
        numbers = numbers.replace(' ', '')
        numbers = numbers.split(',')
        lucky = [str(random.randint(0, 9)), str(random.randint(0, 9)), str(random.randint(0, 9))]
        lol = ""
        for x in lucky:
            lol += f"{x}, "
        if numbers == lucky:
            em = discord.Embed(color=discord.Color(value=0x00ff00), title='You are the lucky winner!')
            em.description = 'Awesome job! You are part of the 0.8% population that won the lottery! :tada:'
            await ctx.send(embed=em)
        else:
            em = discord.Embed(color=discord.Color(value=0xf44e42))
            em.description = f"Ouch. You are part of the 99.2% population that didn't cut it! ¯\_(ツ)_/¯\n\nThe winning numbers were: \n```{lol}```"
            await ctx.send(embed=em)



    @commands.command(aliases=['joke', 'badjoke', 'shitjoke'])
    async def horriblejoke(self, ctx):
        """It's a REALLY REALLY bad joke. Trust me."""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://08ad1pao69.execute-api.us-east-1.amazonaws.com/dev/random_joke') as response:
                r = await response.json()
                color = discord.Color(value=0x00ff00)
                em = discord.Embed(color=color, title=r['setup'])
                em.description = r['punchline']
                em.set_footer(text="Ha. Ha. Ha. Very funny, huh?")
                await ctx.send(embed=em)

    
    @commands.command(aliases=['triggered'])
    async def triggeredpic(self, ctx, user: discord.Member = None):
        """TRI GER RED!!!"""
        if user is None:
            user = ctx.author
        try:
            client = idioticapi.Client(self.client, dev=True)
            av = self.format_avatar(user.avatar_url)
            await ctx.send(file=discord.File(await client.triggered(av), "triggered.gif"))
        except Exception as e:
            await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")


    @commands.command()
    async def batslap(self, ctx, user: discord.Member = None): 
        """User 1 will be slapping, user 2 will BE SLAPPED! Tehehe!"""
        if user is None:
            await ctx.send("Gotta tag someone that you wanna slap!")
        else:
            try:
                client = idioticapi.Client(self.client, dev=True)
                av = self.format_avatar(user.avatar_url)
                avatar = self.format_avatar(ctx.author.avatar_url)
                await ctx.send(file=discord.File(await client.bat_slap(avatar, av), "batslap.png"))
            except Exception as e:
                await ctx.send(f"An error occured with IdioticAPI. \nMore details: \n{e}")

       
       
    @commands.command()
    async def hack(self, ctx, user: discord.Member):
        """Hack someone's account! Try it!"""
        msg = await ctx.send(f"Hacking! Target: {user}")
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
        await msg.edit(content=f"An error has occurred hacking {user}'s account. Please try again later. ❌")   
   
    
    @commands.command()
    async def roast(self, ctx, user: discord.Member = None):
        '''Roast someone! If you suck at roasting them yourself.'''
        roasts = ["I'd give you a nasty look but you've already got one.", "If you're going to be two-faced, at least make one of them pretty.", "The only way you'll ever get laid is if you crawl up a chicken's ass and wait.", "It looks like your face caught fire and someone tried to put it out with a hammer.", "I'd like to see things from your point of view, but I can't seem to get my head that far up your ass.", "Scientists say the universe is made up of neutrons, protons and electrons. They forgot to mention morons.", "Why is it acceptable for you to be an idiot but not for me to point it out?", "Just because you have one doesn't mean you need to act like one.", "Someday you'll go far... and I hope you stay there.", "Which sexual position produces the ugliest children? Ask your mother.", "No, those pants don't make you look fatter - how could they?", "Save your breath - you'll need it to blow up your date.", "If you really want to know about mistakes, you should ask your parents.", "Whatever kind of look you were going for, you missed.", "Hey, you have something on your chin... no, the 3rd one down.", "I don't know what makes you so stupid, but it really works.", "You are proof that evolution can go in reverse.", "Brains aren't everything. In your case they're nothing.", "I thought of you today. It reminded me to take the garbage out.", "You're so ugly when you look in the mirror, your reflection looks away.", "Quick - check your face! I just found your nose in my business.", "It's better to let someone think you're stupid than open your mouth and prove it.", "You're such a beautiful, intelligent, wonderful person. Oh I'm sorry, I thought we were having a lying competition.", "I'd slap you but I don't want to make your face look any better.", "You have the right to remain silent because whatever you say will probably be stupid anyway."]
        await ctx.send(f"Hey, {user.mention}! {random.choice(roasts)}")


    @commands.command()
    async def yomomma(self, ctx):
        '''Sends a random yo momma joke. Outdated?'''
        async with aiohttp.ClientSession() as session:
            async with session.get("http://api.yomomma.info/") as resp:
                resp = await resp.json(content_type=None)
                await ctx.send(resp['joke'])




    @commands.command(aliases=['animation', 'a'])
    async def anim(self, ctx, Type):
        """Animations! Usage: *anim [type]. For a list, use *anim list."""
        if Type is None:
            await ctx.send('Probably a really cool animation, but we have not added them yet! But hang in there! You never know... For a current list, type *anim list')
        else:
            if Type.lower() == 'wtf':
                msg = await ctx.send("```W```")
                await asyncio.sleep(1)
                await msg.edit(content="```WO```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT D```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT DA```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT DA F```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT DA FU```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT DA FUK```")
                await asyncio.sleep(1)
                await msg.edit(content="```WOT DA FUK!```")
                await asyncio.sleep(1)
                await msg.edit(content="WOT DA FUK!")
            elif Type.lower() == 'mom':
                msg = await ctx.send("```Y```")
                await asyncio.sleep(1)
                await msg.edit(content="```YO```")
                await asyncio.sleep(1)
                await msg.edit(content="```YO M```")
                await asyncio.sleep(1)
                await msg.edit(content="```YO MO```")
                await asyncio.sleep(1)
                await msg.edit(content="```YO MOM```")
                await asyncio.sleep(1)
                await msg.edit(content="```YO MOM!```")
                await asyncio.sleep(1)
                await msg.edit(content="YO MOM!")
            elif Type.lower() == 'gethelp':
                msg = await ctx.send("```STOP!```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! G```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Ge```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get s```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get so```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get som```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get some```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get some HELP```")
                await asyncio.sleep(1)
                await msg.edit(content="```STOP! Get some HELP!!!```")
                await asyncio.sleep(1)
                await msg.edit(content="STOP! Get some HELP!!!")
            elif Type.lower() == 'sike':
                msg = await ctx.send("```W```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wa```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wai```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wait```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wait.```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wait..```")
                await asyncio.sleep(1)
                await msg.edit(content="```Wait...```")
                await asyncio.sleep(1)
                await msg.edit(content="```SIKE!```")
                await asyncio.sleep(1)
                await msg.edit(content="SIKE!")
            elif Type.lower() == 'gitgud':
                msg = await ctx.send("```G```")
                await asyncio.sleep(1)
                await msg.edit(content="```Gi```")
                await asyncio.sleep(1)
                await msg.edit(content="```Git```")
                await asyncio.sleep(1)
                await msg.edit(content="```Git GUD!```")
                await asyncio.sleep(1)
                await msg.edit(content="Git GUD!")
            elif Type.lower() == 'clock':
                msg = await ctx.send(":clock12:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock1230:") 
                await asyncio.sleep(1)
                await msg.edit(content=":clock1:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock130:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock2:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock230:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock3:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock330:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock4:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock430:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock5:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock530:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock6:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock630:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock7:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock730:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock8:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock830:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock9:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock930:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock10:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock1030:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock11:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock1130:")
                await asyncio.sleep(1)
                await msg.edit(content=":clock12:")
            elif Type.lower() == 'mate':
                msg = await ctx.send("```Y```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye W```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye WO```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye WOT```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye WOT M8```")
                await asyncio.sleep(1)
                await msg.edit(content="```Ye WOT M8?!?!?!")
                await asyncio.sleep(1)
                await msg.edit(content="Ye WOT M8?!?!?!")
            elif Type.lower() == 'oj':
                msg = await ctx.send("```M```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mm```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm i```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it'```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it's```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it's a```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it's a ORANGE```")
                await asyncio.sleep(1)
                await msg.edit(content="```Mmm it's a ORANGE JUICE```")
                await asyncio.sleep(1)
                await msg.edit(content="Mmm it's a ORANGE JUICE")             
            elif Type.lower() == 'list':
                color = discord.Color(value=0x00ff00)
                em=discord.Embed(color=color, title="Current List of Awesome Animations:")
                em.description = "wtf (anim wtf), mom (anim mom), gethelp (anim gethelp), sike (anim sike), gitgud (anim gitgud), clock (anim clock), mate (anim mate), oj (anim oj)."
                em.set_footer(text="We will always be adding new animations!")
                await ctx.send(embed=em)
            else:
                await ctx.send('Probably a really cool animation, but we have not added them yet! But hang in there! You never know... For a current list, type *anim list')             
              
   
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
        




def setup(bot):
    bot.add_cog(fun(bot))
