import discord
import sys
import os
import io
import asyncio
import aiohttp
import random
import subprocess
import json
import ezjson
import box
import inspect
import traceback
from contextlib import redirect_stdout
from collections import Counter
from inspect import getsource
from discord.ext import commands


class Developer(commands.Cog):
    def __init__(self, bot):
       self.bot = bot
       self.sessions = set()


    def dev_check(self, id):
        with open('data/devs.json') as f:
            devs = json.load(f)
            if id in devs:
                return True
        return False
    
    
    def owner_check(self, id):
        if id == 277981712989028353:
            return True
        return False
       

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')


    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'
       
    
    @commands.command()
    async def presence(self, ctx, *, message=None):
        """Change the bot's presence."""
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        if not message:
            await bot.change_presence(activity=discord.Game(name=f"uwu help | {len(bot.guilds)} servers"))
            return await ctx.send()
        else:
            await bot.change_presence(activity=discord.Game(name=f"uwu help | {len(bot.guilds)} servers | {message}"))


    @commands.command()
    async def error(self, ctx, code):
        """Gets info on an error by code."""
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        data = await self.bot.db.errors.find_one({"code": code})
        if not data:
            return await ctx.send("No error with that code was found. Check it!")
        data = box.Box(data)
        if len(data.error) < 2000:
            err = data.error
        else:
            resp = await self.session.post("https://hastebin.com/documents", data=data.error)
            resp = await resp.json()
            err = f"**The error message is too long to fit! The error has been uploaded to Hastebin:\n\nhttps://hastebin.com/{resp['key']}"
        guild = self.bot.get_guild(data.guild)
        em = discord.Embed(color=ctx.author.color, title="Error Information")
        em.description = f"**Traceback**\n\n```\n{err}```"
        em.add_field(name="Code", value=f"**{code}**", inline=True)
        em.add_field(name="Server", value=guild)
        em.add_field(name="Channel", value=f"#{data.channel}\n(Invite: {data.invite})")
        em.add_field(name="User", value=data.user)
        em.add_field(name="Command Content", value=data.content)
        await ctx.send(embed=em)

    @commands.command(hidden=True)
    async def causeerror(self, ctx):
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        [][0]

    @commands.command(hidden=True)
    async def psa(self, ctx, *, msg: str = None):
        """Sends an announcement to a channel in every server."""
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        await ctx.send("I have began to send the PSA to all servers I'm in! This will take a while. You can track my progress in <#513368885144190986>.", edit=False)
        for x in self.bot.guilds:
            for i in range(len(x.channels)):
                try:
                    await x.channels[i].send(f"__**Public Service Announcement**__\n\n{msg}")
                    await self.bot.get_channel(513368885144190986).send(f"PSA sent to **{x.name}**. Channel: #{x.channels[i].name}")
                    break
                except:
                    continue
        await ctx.send(f"I have sent the PSA to every server! {self.bot.get_emoji(453322013591863316)}", edit=False)



       
    @commands.command()
    async def shutdown(self, ctx):
        """Shuts DOWN the bot. Cya!"""
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        msg = await ctx.send(f"Shutting down... {self.bot.get_emoji(441385713091477504)}")
        await asyncio.sleep(1)
        await msg.edit(content="Goodbye! :wave:")
        await self.bot.logout()


    @commands.command(hidden=True)
    async def restart(self, ctx):
        """Restarts the bot. Be Back S00N"""
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        msg = await ctx.send(f"Restarting... {self.bot.get_emoji(471279983197814806)}")
        with open("restart.txt", "w") as f:
            f.write(f"{ctx.channel.id}\n{msg.id}")
        os.execv(sys.executable, ['python'] + ['bot.py'])
        
    #@command.commands(hidden=True)
    #async def token(self, ctx):
        #if not self.dev_check(ctx.author.id):
            #return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        #await ctx.send(f"{bot.ws.token}"
       
       
    
    @commands.command(hidden=True)
    async def changename(self, ctx, name=None):
        """Changes my name. Please make it good!"""
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        if name is None:
            return await ctx.send("Hmm...my name cannot be blank!")
        else:
            await self.bot.user.edit(username=f'{name}')


    @commands.command(name='exec', hidden=True)
    async def _exec(self, ctx, *, code):
        """Executes code like the Command Line."""
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        e = discord.Embed(color=0x00ff00, title='Running code')
        e.description = f'Please wait... {self.bot.get_emoji(471279983197814806)}'
        msg = await ctx.send(embed=e)
        lol = subprocess.run(f"{code}", cwd=os.getcwd(), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        err = lol.stderr.decode("utf-8")
        res = lol.stdout.decode("utf-8")
        em = discord.Embed(color=0x00ff00, title='Ran on the Command Prompt!')
        if len(res) > 1850 or len(err) > 1850:
            em.description = f"Ran on the Command Line ```{code}``` Output: \nThe process details are too large to fit in a message."
            await msg.edit(embed=em)
        else:
            em.description = f"Ran on the Command Line: ```{code}``` Output: \n\n```{err or res}```"
            await msg.edit(embed=em)

    @commands.command(hidden=True)
    async def update(self, ctx, update_flag: str = None):
        """Updates the bot. Ez!"""
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        msg = await ctx.send(f"Updating... {self.bot.get_emoji(471279983197814806)}")
        try:
            lol = subprocess.run("git pull", cwd=os.getcwd(), stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
            for cog in self.bot.cogs:
                cog = cog.lower()
                self.bot.unload_extension(f"cogs.{cog}")
                self.bot.load_extension(f"cogs.{cog}")
            await msg.edit(content=f"All cogs reloaded, and READY TO ROLL! :white_check_mark: \n\nLog:\n```{lol}```")
            if update_flag == "--restart":
                msg = await ctx.send(f"Restarting... {self.bot.get_emoji(471279983197814806)}")
                with open("restart.txt", "w") as f:
                    f.write(f"{ctx.channel.id}\n{msg.id}")
                subprocess.run("pm2 restart 0", cwd=os.getcwd(), stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
        except Exception as e:
            await msg.edit(content=f"An error occured. :x: \n\nDetails: \n{e}")


    @commands.command(hidden=True)
    async def loadcog(self, ctx, cog):
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        else:
            msg = await ctx.send(f"Loading cog `{cog}`... :arrows_counterclockwise:")
            try:
                self.bot.load_extension(f"cogs.{cog}")
                await msg.edit(content="Loaded the cog! :white_check_mark:")
            except Exception as e:
                await msg.edit(content=f"An error occured. Details: \n{e}")


    @commands.command(hidden=True)
    async def unloadcog(self, ctx, cog):
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        msg = await ctx.send(f"Unloading cog `{cog}`... :arrows_counterclockwise:")
        try:
            self.bot.unload_extension(f"cogs.{cog}")
            await msg.edit(content="Unloaded the cog! :white_check_mark:")
        except Exception as e:
            await msg.edit(content=f"An error occured. Details: \n{e}")

    @commands.command(hidden=True)
    async def reloadcog(self, ctx, cog=None):
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        msg = await ctx.send(f"Reloading cog `{cog}`... :arrows_counterclockwise:")
        try:
            self.bot.unload_extension(f"cogs.{cog}")
            self.bot.load_extension(f"cogs.{cog}")
            await msg.edit(content="Reloaded the cog! :white_check_mark:")
        except Exception as e:
            await msg.edit(content=f"An error occured. Details: \n{e}")

    @commands.command()
    async def blacklist(self, ctx, user: discord.User):
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        await self.bot.db.blacklist.update_one({"id": user.id}, {"$set": {"status": True}}, upsert=True)
        await ctx.send(f"Successfully blacklisted **{str(user)}** from the bot.")

    @commands.command()
    async def unblacklist(self, ctx, user: discord.User):
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        await self.bot.db.blacklist.update_one({"id": user.id}, {"$set": {"status": False}}, upsert=True)
        await ctx.send(f"Successfully removed **{str(user)}** from the blacklist.")

    @commands.command(hidden=True)
    async def source(self, ctx, command):
        """Get the source to any command"""
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        cmd = self.bot.get_command(command)
        if cmd is None:
            return await ctx.send("Could not find that command.")
        await ctx.send(f"```py\n{getsource(cmd.callback)}```")


    @commands.command(hidden=True)
    async def sudo(self, ctx, user: discord.Member, *, command: str):
        if not self.dev_check(ctx.author.id):
            return

        ctx.message.author = user
        ctx.message.content = f"{ctx.prefix}{command}"
        await self.bot.process_commands(ctx.message)



    @commands.command(pass_context=True, hidden=True)
    async def repl(self, ctx):
        """Launches an interactive REPL session."""
        if not self.dev_check(ctx.author.id):
            return await ctx.send(f"Sorry, but you can't run this command because you ain't a developer! {self.bot.get_emoji(691757044361068574)}")
        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': ctx.message,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author,
            '_': None,
        }

        if ctx.channel.id in self.sessions:
            await ctx.send('Already running a REPL session in this channel. Exit it with `quit`.', edit=False)
            return

        self.sessions.add(ctx.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit()` or `quit` to exit.', edit=False)

        def check(m):
            return m.author.id == ctx.author.id and \
                   m.channel.id == ctx.channel.id and \
                   m.content.startswith('`')

        while True:
            try:
                response = await self.bot.wait_for('message', check=check, timeout=10.0 * 60.0)
            except asyncio.TimeoutError:
                await ctx.send('Exiting REPL session.', edit=False)
                self.sessions.remove(ctx.channel.id)
                break

            cleaned = self.cleanup_code(response.content)

            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.send('Exiting.', edit=False)
                self.sessions.remove(ctx.channel.id)
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    await ctx.send(self.get_syntax_error(e))
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                fmt = f'```py\n{value}{traceback.format_exc()}\n```'
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = f'```py\n{value}{result}\n```'
                    variables['_'] = result
                elif value:
                    fmt = f'```py\n{value}\n```'

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        await ctx.send('Content too big to be printed.')
                    else:
                        await ctx.send(fmt)
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await ctx.send(f'Unexpected error: `{e}`')

    @commands.command(hidden=True)
    async def massdm(self, ctx): 
        if not self.dev_check(ctx.author.id): return
        dbl = self.bot.get_guild(264445053596991498)
        users = [x for x in self.bot.users if not dbl.get_member(x.id)]
        await ctx.send("Starting....")
        for user in users:
            try:
                await user.send(f"""
Hiya, **{user.name}**! 

Really sorry to bother you, as I know this may be intrusive. Just take a few moments to read what I have to say!

Unfortunately, I will be deleted by Discord soon as my owner's account has been permanently disabled. Just letting you know, I am not over yet! However, you can **add the NEW BOT USER to your server, which has the same features as the old one.**. Here's the invite link below for your convenience:

https://discordapp.com/api/oauth2/authorize?client_id=520682706896683009&permissions=8&scope=bot

I still have the same features, such as custom config, mod, fun, utility, music, automods, anime, and so much more, so check me out. One thing to note is that **my default prefix will be `b.` (or mention).** You can still customize it for yourselves.

If you have any issues, or just wanna chill out for fun, don't forget to join my awesome senpai's server:

https://discord.gg/3Nxb7yZ

Have an awesome day! WOOP!""")
                await self.bot.get_channel(513368885144190986).send(f"Sent message to **{user.name}**.")
            except:
                await self.bot.get_channel(513368885144190986).send(f"Could not send message to **{user.name}**.")


def setup(bot): 
    bot.add_cog(Developer(bot))   
    
