import discord
import asyncio
import random
import textwrap
import wikipedia
import urllib.parse
import json
import re
import box
import math
import openweathermapy.core as weather
from bs4 import BeautifulSoup
from pygoogling.googling import GoogleSearch
from discord.ext import commands
from mtranslate import translate
from .utils.paginator import Pages
from .utils.utils import Utils
from discord.ext.commands.cooldowns import BucketType
from py_expression_eval import Parser

class Utility:
    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.session
        with open("data/apikeys.json") as f:
            x = json.load(f)
        self.weather_api = x['weatherapi']
        self.langs = {
            "ab": "Abkhaz",
            "aa": "Afar",
            "af": "Afrikaans",
            "ak": "Akan",
            "sq": "Albanian",
            "am": "Amharic",
            "ar": "Arabic",
            "an": "Aragonese",
            "hy": "Armenian",
            "as": "Assamese",
            "av": "Avaric",
            "ae": "Avestan",
            "ay": "Aymara",
            "az": "Azerbaijani",
            "bm": "Bambara",
            "ba": "Bashkir",
            "eu": "Basque",
            "be": "Belarusian",
            "bn": "Bengali",
            "bh": "Bihari",
            "bi": "Bislama",
            "bs": "Bosnian",
            "br": "Breton",
            "bg": "Bulgarian",
            "my": "Burmese",
            "ca": "Catalan",
            "ch": "Chamorro",
            "ce": "Chechen",
            "ny": "Nyanja",
            "zh": "Chinese",
            "cv": "Chuvash",
            "kw": "Cornish",
            "co": "Corsican",
            "cr": "Cree",
            "hr": "Croatian",
            "cs": "Czech",
            "da": "Danish",
            "dv": "Divehi",
            "nl": "Dutch",
            "dz": "Dzongkha",
            "en": "English",
            "eo": "Esperanto",
            "et": "Estonian",
            "ee": "Ewe",
            "fo": "Faroese",
            "fj": "Fijian",
            "fi": "Finnish",
            "fr": "French",
            "ff": "Fula",
            "gl": "Galician",
            "ka": "Georgian",
            "de": "German",
            "el": "Greek",
            "gn": "Guarani",
            "gu": "Gujarati",
            "ht": "Haitian",
            "ha": "Hausa",
            "he": "Hebrew",
            "hz": "Herero",
            "hi": "Hindi",
            "ho": "Hiri-Motu",
            "hu": "Hungarian",
            "ia": "Interlingua",
            "id": "Indonesian",
            "ie": "Interlingue",
            "ga": "Irish",
            "ig": "Igbo",
            "ik": "Inupiaq",
            "io": "Ido",
            "is": "Icelandic",
            "it": "Italian",
            "iu": "Inuktitut",
            "ja": "Japanese",
            "jv": "Javanese",
            "kl": "Kalaallisut",
            "kn": "Kannada",
            "kr": "Kanuri",
            "ks": "Kashmiri",
            "kk": "Kazakh",
            "km": "Khmer",
            "ki": "Kikuyu",
            "rw": "Kinyarwanda",
            "ky": "Kyrgyz",
            "kv": "Komi",
            "kg": "Kongo",
            "ko": "Korean",
            "ku": "Kurdish",
            "kj": "Kwanyama",
            "la": "Latin",
            "lb": "Luxembourgish",
            "lg": "Luganda",
            "li": "Limburgish",
            "ln": "Lingala",
            "lo": "Lao",
            "lt": "Lithuanian",
            "lu": "Luba-Katanga",
            "lv": "Latvian",
            "gv": "Manx",
            "mk": "Macedonian",
            "mg": "Malagasy",
            "ms": "Malay",
            "ml": "Malayalam",
            "mt": "Maltese",
            "mi": "M\u0101ori",
            "mr": "Marathi",
            "mh": "Marshallese",
            "mn": "Mongolian",
            "na": "Nauru",
            "nv": "Navajo",
            "nb": "Norwegian Bokm\u00e5l",
            "nd": "North-Ndebele",
            "ne": "Nepali",
            "ng": "Ndonga",
            "nn": "Norwegian-Nynorsk",
            "no": "Norwegian",
            "ii": "Nuosu",
            "nr": "South-Ndebele",
            "oc": "Occitan",
            "oj": "Ojibwe",
            "cu": "Old-Church-Slavonic",
            "om": "Oromo",
            "or": "Oriya",
            "os": "Ossetian",
            "pa": "Panjabi",
            "pi": "P\u0101li",
            "fa": "Persian",
            "pl": "Polish",
            "ps": "Pashto",
            "pt": "Portuguese",
            "qu": "Quechua",
            "rm": "Romansh",
            "rn": "Kirundi",
            "ro": "Romanian",
            "ru": "Russian",
            "sa": "Sanskrit",
            "sc": "Sardinian",
            "sd": "Sindhi",
            "se": "Northern-Sami",
            "sm": "Samoan",
            "sg": "Sango",
            "sr": "Serbian",
            "gd": "Scottish-Gaelic",
            "sn": "Shona",
            "si": "Sinhala",
            "sk": "Slovak",
            "sl": "Slovene",
            "so": "Somali",
            "st": "Southern-Sotho",
            "es": "Spanish",
            "su": "Sundanese",
            "sw": "Swahili",
            "ss": "Swati",
            "sv": "Swedish",
            "ta": "Tamil",
            "te": "Telugu",
            "tg": "Tajik",
            "th": "Thai",
            "ti": "Tigrinya",
            "bo": "Tibetan",
            "tk": "Turkmen",
            "tl": "Tagalog",
            "tn": "Tswana",
            "to": "Tonga",
            "tr": "Turkish",
            "ts": "Tsonga",
            "tt": "Tatar",
            "tw": "Twi",
            "ty": "Tahitian",
            "ug": "Uighur",
            "uk": "Ukrainian",
            "ur": "Urdu",
            "uz": "Uzbek",
            "ve": "Venda",
            "vi": "Vietnamese",
            "vo": "Volapuk",
            "wa": "Walloon",
            "cy": "Welsh",
            "wo": "Wolof",
            "fy": "Western-Frisian",
            "xh": "Xhosa",
            "yi": "Yiddish",
            "yo": "Yoruba",
            "za": "Zhuang",
            "zu": "Zulu"
        }
        self.utils = Utils(self.bot)

    def cleanup_code(self, content):
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    async def get_tag(self, guild_id, name):
        data = await self.bot.db.tags.find_one({"id": guild_id})
        if not data:
            return None
        try:
            match = [x for x in data['data'] if x['name'] == name][0]
        except IndexError:
            return None
        else:
            return match

    @commands.command(aliases=["stealav"])
    async def stealavatar(self, ctx, ID):
        """Get the URL of anyone's avatar!"""
        user = await self.bot.get_user_info(ID)
        if not user:
            return await ctx.send("It looks like that is not a valid ID! Better check it.")
        em = discord.Embed(color=ctx.author.color, title=f"{user.name}'s avatar")
        em.set_image(url=user.avatar_url)
        await ctx.send(embed=em)

    @commands.command(aliases=["gh", "buhtig"])
    async def github(self, ctx, username: str, repo: str):
        """Search GitHub for a repo made by a user."""
        res = await self.bot.session.get(f"https://api.github.com/repos/{username}/{repo}")
        res = await res.json()
        res = box.Box(res)
        if res.get("message", "") == "Not Found":
            return await ctx.send("The repo doesn't exist. Or maybe it's private. Either way, there's a reason for it. :smirk:")
        size = f"{res.size} KB" if res.size <= 1024 else f"{(res.size / 1024 / 1024):.2f} GB" if math.floor(res.size / 1024) > 1024 else f"{(res.size / 1024):.2f} MB"
        
        lic = f"[{res.license.name}]({res.license.url})" if res.license and res.license.name and res.license.url else res.license.name if res.license else "No license."
        fork = f"This repository is a **fork** of [{res.parent.full_name}]({res.parent.html_url})" if res.fork else None
        archived = "This repository is **archived** and is now **read-only.**" if res.archived else None
        desc = f"""
__**Description**__
{res.description or 'No README found.'}

:pencil: **Language:** {res.language}
:star: **Stars:** {res.stargazers_count}
:fork_and_knife: **Forks:** {res.forks_count}
:eyes: **Watchers:** {res.subscribers_count}
:hammer_pick: **License:** {lic}
:exclamation: **Issues:** {res.open_issues}
:gift: **Size:** {size}
"""
        if fork:
            desc += f"\n❯ {fork}"
        if archived:
            desc += f"\n❯ {archived}"
        em = discord.Embed(color=discord.Color(value=0x00ff00), title=res.name)
        em.set_author(name=res.owner.login, icon_url=res.owner.avatar_url)
        em.description = desc
        em.set_footer(text=f"Powered by Github API | Requested by: {str(ctx.author)}", icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
        await ctx.send(embed=em)

    
    @commands.command(aliases=["iinfo"])
    async def inviteinfo(self, ctx, invite: str):
        try:
            info = await self.bot.get_invite(invite)
        except:
            return await ctx.send("NANI? The invite you gave is invalid.")
        em = discord.Embed(color=ctx.author.color, title="Invite Information")
        em.description = info.url
        em.add_field(name="Server", value=info.guild.name, inline=False)
        em.add_field(name="Channel", value=f"#{info.channel.name}")
        em.add_field(name="Max Uses", value=info.max_uses or "Unlimited")
        em.add_field(name="Total Uses", value=info.uses)
        em.add_field(name="Temporary Invite", value="Yes" if info.temporary else "No")
        em.add_field(name="Created By", value=str(info.inviter))
        em.add_field(name="Revoked", value="Yes" if info.revoked else "No")
        await ctx.send(embed=em)

    @commands.command()
    async def snipe(self, ctx, channel: str = None):
        """Gets the last deleted message in the channel."""
        if ctx.guild.id == 392149566012784650:
            if not ctx.author.guild_permissions.manage_guild:
                return await ctx.send("You don't have the permissions! Get some or get out. :)")
        if not channel:
            channel = ctx.channel
        else:
            channel = self.bot.get_channel(int(channel.replace("<#", "").replace(">", ""))) 
        try:
            snipes = self.bot.snipes[str(channel.id)]
        except KeyError:
            return await ctx.send("No one deleted a message yet, since the bot was last up. Is the channel dead?")
        msgs = []
        for x in snipes:
            msgs.append(f"**Sent By:** {str(x['author'])}\n\n{x['content']}\n\n**Sent At:** {str(x['message'].created_at.strftime('%A, %b %d, %Y %I:%M %p'))}")
        pg = Pages(ctx, entries=msgs, per_page=1)
        pg.embed.title = "Sniped Message"

        await pg.paginate()

    
    @commands.command()
    async def editsnipe(self, ctx, channel: int = None):
        """Gets the messages that were edited since the bot's last restart."""
        if not channel:
            channel = ctx.channel
        else:
            channel = self.bot.get_channel(int(channel.replace("<#", "").replace(">", ""))) 
        try:
            snipes = self.bot.editsnipes[str(channel.id)]
        except KeyError:
            return await ctx.send("No one deleted a message yet, since the bot was last up. Is the channel dead?")
        msgs = []
        for x in snipes:
            msgs.append(f"""
**Sent By:** {str(x['author'])}

**Before**
**Sent At:** {str(x['before_message'].created_at.strftime('%A, %b %d, %Y %I:%M %p'))}
{x['before']}

**After**
**Sent At:** {str(x['after_message'].created_at.strftime('%A, %b %d, %Y %I:%M %p'))}
{x['after']}
""")
        pg = Pages(ctx, entries=msgs, per_page=1)
        pg.embed.title = "Sniped Edited Message"
        await pg.paginate()

    @commands.command(aliases=['invites', 'invitelist'])
    async def serverinvites(self, ctx):
        """Get info on all the invites in a server."""
        await ctx.trigger_typing()
        content = []
        uses = 0
        invites = await ctx.guild.invites()
        for x in invites:
             uses += x.uses
        for x in invites:
            content.append(f"""
**{x.code}**
**Made By:** {str(x.inviter)}
**Channel:** #{x.channel.name}
**Created At:** {str(x.created_at.strftime("%b %d, %Y, %A, %I:%M %p"))}
**Max Uses:** {x.max_uses or "Unlimited"}
**Temporary:** {"Yes" if x.temporary else "No"}
**Total Uses:** {x.uses}\n

**Total Uses (Of all invites): {uses}**
""")
           
        pg = Pages(ctx, entries=content, per_page=1)
        pg.embed.title = "Server Invites"
        pg.embed.set_footer(text=f"Total Invite Uses: {uses}")
        await pg.paginate()

    @commands.command(aliases=['finddiscrim', 'disc', 'discriminator'])
    async def discrim(self, ctx, disc: str):
        """Find users that have the discriminator given."""
        users = [str(x) for x in self.bot.users if x.discriminator == disc]
        pg = Pages(ctx, entries=users, per_page=10)
        pg.embed.title = f"Users with Discriminator: {disc}"
        pg.embed.set_footer(text=f"Total: {len(users)} users")
        await pg.paginate()


    @commands.command(aliases=['math', 'calculate'])
    async def calc(self, ctx, *, expression):
        """Do regular math like a regular normie."""
        parser = Parser()
        variables = {
            "pi": math.pi,
            "e": math.e
        }
        try:
            res = parser.parse(expression).evaluate(variables)
        except OverflowError:
            emb = discord.Embed(color=0xf44242, title="Math Error")
            emb.description = f"""
:inbox_tray: **Input**
```{expression}```

:outbox_tray: **Output**
The calculated number is too large to be represented."""
            return await ctx.send(embed=emb)
        except:
            embe = discord.Embed(color=0xf44242, title="Math Error")
            embe.description = f"""
:inbox_tray: **Input**
```{expression}```

:outbox_tray: **Output**
Invalid math expression."""
            return await ctx.send(embed=embe)
        em = discord.Embed(color=0x00ff00, title="Math Evaluated")
        em.description = f"""
:inbox_tray: **Input**
```{expression}```

:outbox_tray: **Output**
```{res}```"""
        return await ctx.send(embed=em)



    @commands.command(aliases=['dict'])
    @commands.cooldown(1, 5.0, BucketType.user)
    async def dictionary(self, ctx, *, word):
        """Search a word on Oxford Dictionary."""
        headers = {
            "app_id": self.bot.config.dictionaryapi_id,
            "app_key": self.bot.config.dictionaryapi_key
        }
        resp = await self.bot.session.get(f"https://od-api.oxforddictionaries.com/api/v1/entries/en/{word}",headers=headers)
        try:
            resp = box.Box(await resp.json())
        except:
            return await ctx.send("No definitions with this word exist.")
        definitions = []
        for x in range(len(resp.results[0].lexicalEntries)):
            definitions.append(f"""
**{resp.results[0].word}** ({resp.results[0].lexicalEntries[x].pronunciations[0].phoneticSpelling})

*{resp.results[0].lexicalEntries[x].lexicalCategory}*
{resp.results[0].lexicalEntries[x].entries[0].senses[0].definitions[0]}
""")

        d = Pages(ctx, entries=definitions, per_page=1)
        await d.paginate()


    
    @commands.command()
    async def afk(self, ctx, action=None, *, status: commands.clean_content() = None):
        """View your AFK status."""
        if not action and not status:
            em = discord.Embed(color=ctx.author.color, title="AFK Status")
            data = await self.bot.db.afk.find_one({"id": ctx.author.id})
            if not data:
                em.description = "You aren't AFK at the moment!"
            else:
                if not data['status']:
                    em.description = "You aren't AFK at the moment!"
                else:
                    em.description = data['status']
            return await ctx.send(embed=em)
        elif action.lower() == "set":
            await self.bot.db.afk.update_one({"id": ctx.author.id}, {"$set": {"status": status}}, upsert=True)
            return await ctx.send(f":sleeping: Your AFK status has been set to **{status}**.\n\nAnyone who pings you while I'm there will get notified about what you're doing!")
        elif action.lower() == "reset" or action.lower() == "clear":
            await self.bot.db.afk.update_one({"id": ctx.author.id}, {"$set": {"status": False}}, upsert=True)
            return await ctx.send(":smiley: You are no longer AFK!")
        else:
            return await ctx.send("""
**AFK Command**

*afk -> Check your AFK status.

*afk set [status] -> Turn on AFK and set your status.

*afk reset -> Turn off AFK.
            """)




    @commands.command(aliases=['g', 'gg'])
    async def google(self, ctx, *, query: str):
        """Searches google for a query"""
        # Shoutout to Free TNT#5796 for this code. Thanks!
        safe = "on"
        if not isinstance(ctx.channel, discord.DMChannel) and ctx.channel.nsfw:
            safe = "off"
        params = {"q": query, "safe": safe}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"}
        try:
            async with ctx.typing():
                res = await self.bot.session.get("https://google.com/search", params=params, headers=headers)
                if res.status != 200:
                    return await ctx.send("Google has failed to respond.")
                html = await res.text()
                data = BeautifulSoup(html, "lxml")
                a = data.find_all("h3", {"class": "r"})
                if len(a) < 1:
                    return await ctx.send(f"Oops! Looks like no results were found with your search term **{query}**.")
                res = ""
                counter = 0
                for elem in a:
                    if counter >= 5:
                       break
                    url = elem.find("a")
                    if not url:
                        continue
                    url = url.get("href")
                    if not url:
                        continue
                    regex = r".*(&sa=.*)"
                    m = re.match(regex, url)
                    if m:
                        url = url.replace(m.group(1), "")
                    url = url.replace("/url?q=", "")
                    res += "**{}** \n{}\n\n".format(elem.text, url)
                    counter += 1
                if not res:
                    return await ctx.send("No results found.")
                em = discord.Embed(color=ctx.author.color)
                em.title = f"Google Search: {self.utils.slice_text(query, 100)}"
                em.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
                em.description = self.utils.slice_text(res, 2000) + f"\n\nSafeSearch is **{safe}**.\nIt is disabled in NSFW channels and enabled for regular channels and DMs."
                await ctx.send(embed=em)
        except:
            await ctx.send("Something went wrong, please try again later.")
        # search = GoogleSearch(query)
        # search.start_search()
        # result = search.search_result
        # em = discord.Embed(color=0x00ff00, title=f'Google Search Results for: {query}')
        # if result == []:
        #     em.description = "No results for this search term was found. :x:"
        #     return await ctx.send(embed=em)
        # else:
        #     em.description = f"**Top Result:**\n{result[0]}\n\n**Other Results:**\n{result[1]}\n{result[2]}\n{result[3]}\n{result[4]}\n{result[5]}"
        # em.set_author(name=f"Searched by: {ctx.author.name}", icon_url=ctx.author.avatar_url)
        # lol = []
        # for x in result:
        #     lol.append(f"{x}\n")
        # page = Pages(ctx, entries=lol, per_page=5)
        # await page.paginate()


    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, *, name: str):
        """Get a tag by its name."""
        stuff = await self.get_tag(ctx.guild.id, name)
        if not stuff:
            return await ctx.send("No tag was found with this name! Maybe be the first to create one... :thinking:")
        em = discord.Embed(color=ctx.author.color, title=stuff['name'])
        em.description = stuff['content']
        await ctx.send(embed=em)

    @tag.command(aliases=['add', 'make'])
    #@commands.has_permissions(manage_guild=True)
    async def create(self, ctx, name, *, content):
        """Create a tag in the server."""
        if await self.get_tag(ctx.guild.id, name):
            return await ctx.send("Nope. A tag already exists with this name.")
        stuff = await self.bot.db.tags.find_one({"id": ctx.guild.id})

        if not stuff:
            stuff = await self.bot.db.tags.update_one({"id": ctx.guild.id}, {"$set": {"data": []}}, upsert=True)
        stuff = await self.bot.db.tags.find_one({"id": ctx.guild.id})
        data = {
            "name": name,
            "content": content,
            "author": ctx.author.id
        }
        stuff['data'].append(data)
        await self.bot.db.tags.update_one({"id": ctx.guild.id}, {"$set": stuff}, upsert=True)
        name = await commands.clean_content().convert(ctx, name)
        await ctx.send(f"Successfully created the tag **{name}** for this server. :white_check_mark:")

    @tag.command(aliases=['remove'])
    #@commands.has_permissions(manage_guild=True)
    async def delete(self, ctx, name):
        """Remove an existing tag in the server."""
        stuff = await self.bot.db.tags.find_one({"id": ctx.guild.id})
        to_remove = await self.get_tag(ctx.guild.id, name)
        name = await commands.clean_content().convert(ctx, name)
        if ctx.author.guild_permissions.manage_guild:
            if not to_remove:
                return await ctx.send("No tag with the given name was found for this server. :x:")
            stuff['data'].remove(to_remove)
            await self.bot.db.tags.update_one({"id": ctx.guild.id}, {"$set": stuff}, upsert=True)
            await ctx.send(f"Successfully removed the tag **{name}** for this server. :white_check_mark:")
        else:
            if not to_remove:
                    return await ctx.send("No tag with the given name was found for this server. :x:")
            if to_remove['author'] == ctx.author.id:
                stuff['data'].remove(to_remove)
                
                await self.bot.db.tags.update_one({"id": ctx.guild.id}, {"$set": stuff}, upsert=True)
                await ctx.send(f"Successfully removed the tag **{name}** for this server. :white_check_mark:")
        
            else:
                return await ctx.send("You need **Manage Server** permissions to remove other people's tags.")

    @tag.command(aliases=['show', 'showall'])
    async def all(self, ctx):
        stuff = await self.bot.db.tags.find_one({"id": ctx.guild.id})
        data = stuff['data']
        em = discord.Embed(color=ctx.author.color, title=f"Tags for: {ctx.guild.name}")
        em.description = "\n".join([x['name'] for x in data])
        await ctx.send(embed=em)

    @commands.command(name="translate", aliases=["trans"])
    async def _translate(self, ctx, lang, *, text: str):
        em = discord.Embed(color=ctx.author.color, title="Translated!")
        em.add_field(name="Original Text", value=f"```{text}```", inline=False)
        if lang in self.langs:
            to_translate = translate(text, lang)
        else:
            lang = dict(zip(self.langs.values(), self.langs.keys())).get(lang.lower().title())
            to_translate = translate(text, lang)
        em.add_field(name="Translated Text", value=f"**Language:** {lang}\n\n**Text:**\n```{to_translate}```", inline=False)
        await ctx.send(embed=em)

    @commands.command()
    async def weather(self, ctx, *, city: str):
        """Get the weather for a select city."""
        settings = {"APPID": self.weather_api}
        data = weather.get_current('{}'.format(city), units='metric', **settings)
        loc = data('name')
        country = data('sys.country')
        lon = data('coord.lon')
        lat = data('coord.lat')
        temp = data('main.temp')
        temp2 = temp * 9 / 5 + 32
        high = data('main.temp_max')
        low = data('main.temp_min')
        high2 = high * 9 / 5 + 32
        low2 = low * 9 / 5 + 32
        embed = discord.Embed(title='{}, {}'.format(loc, country), color=ctx.author.color)
        embed.add_field(name='Absolute Location :map:', value='Longitude, Latitude\n{}, {}'.format(lon, lat))
        embed.add_field(name='Temperature :thermometer:', value='{}F, {}C'.format(temp2, temp))
        embed.add_field(name='Humidity :potable_water:', value='{}%'.format(data('main.humidity')))
        embed.add_field(name='Wind Speed :wind_blowing_face: ', value='{}m/s'.format(data('wind.speed')))
        embed.add_field(name='Lowest Temperature :low_brightness: ', value='**{}** F\n**{}** C'.format(low2, low))
        embed.add_field(name='Highest Temperature :high_brightness: ', value='**{}** F\n**{}** C'.format(high2, high))
        embed.set_footer(text='Weather Data from OpenWeatherMap.org')
        embed.set_thumbnail(url='https://cdn2.iconfinder.com/data/icons/weather-icons-8/512/day-clear-256.png')
        await ctx.send(embed=embed)

    @commands.command()
    async def coliru(self, ctx, language: str = None, *, code: str = None):
        """Compiles code through Coliru."""
        if not language and not code:
            return await ctx.send(textwrap.dedent("""
            This will evaluate code through Coliru.

            Usage: *coliru [language] [body]

            Available languages:

            cpp: C++
            c: C
            py / python: Python
            haskell: Haskell
            ruby: Ruby
            lua: Lua

            **Some things to note:**
            -Python only supports v2.7, unfortunately.
            -The C++ compiler uses g++ -std=c++14
            """))
        cmds = {
            'cpp': 'g++ -std=c++1z -O2 -Wall -Wextra -pedantic -pthread main.cpp -lstdc++fs && ./a.out',
            'c': 'mv main.cpp main.c && gcc -std=c11 -O2 -Wall -Wextra -pedantic main.c && ./a.out',
            'py': 'python main.cpp',  # coliru has no python3
            'python': 'python main.cpp',
            'haskell': 'runhaskell main.cpp',
            'ruby': 'ruby main.cpp',
            'lua': 'lua main.cpp',
            'flex': 'mv main.cpp main.c && flex main.c -o lex.c && gcc lex.c -lfl && ./a.out'
        }
        try:
            lang = cmds[language]
        except KeyError:
            return await ctx.send("Invalid language provided. Please choose from cpp, c, py, python, haskell.")
        code = self.cleanup_code(code)
        data = {
            "cmd": lang,
            "src": code
        }
        em = discord.Embed(color=0xf9e236, title='Evaluated!')
        resp = await self.bot.session.post('http://coliru.stacked-crooked.com/compile', json=data)
        output = await resp.text(encoding='utf-8')
        if len(output) < 1992:
            em.description = f"```{output}```"
        else:
            resp = await self.bot.session.post('http://coliru.stacked-crooked.com/share', json=data)
            share_id = await resp.text()
            em.description = f"The result was too large to fit in a message. View the result here:\nhttp://coliru.stacked-crooked.com/a/{share_id}"
        await ctx.send(embed=em)

    @commands.command() # i would make it so that you seperate with a , so its easier for some
    async def poll(self, ctx, *, args):
        """Creates a poll with reactions. Seperate choices with |."""
        if '|' not in args:
            return await ctx.send("Seperate the question and choices with |.\nUsage: *poll What is the question? | Idk. | You tell me.")
        try:
            await ctx.message.delete()
        except:
            pass
        choices = args.split("|")
        desc = ""
        counter = 0
        em = discord.Embed(color=0xf9e236, title=choices[0])
        choices.remove(choices[0])
        if len(choices) > 9:
            return await ctx.send("You can have a maximum of 9 choices for a poll.")
        for x in choices:
            counter += 1
            desc += f"{str(counter)} - {x}\n"
        em.description = desc
        em.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        msg = await ctx.send(embed=em)
        # emojis = {
        #     "1": ":one:",
        #     "2": ":two",
        #     "3": ":three:",
        #     "4": ":four:",
        #     "5": ":five:",
        #     "6": ":six:",
        #     "7": ":seven:",
        #     "8": ":eight:",
        #     "9": ":nine:"
        # }
        counter = 0
        for x in choices:
            counter += 1
            await msg.add_reaction(f"{str(counter)}\u20e3")

    @commands.command(name='wikipedia', aliases=['wiki'])
    async def _wikipedia(self, ctx, *, query):
        em = discord.Embed(color=0xf9e236, title=f"Wikipedia Results for: {query}")
        try:
            res = wikipedia.summary(str(query))
        except wikipedia.exceptions.PageError:
            em = discord.Embed(color=0xf44e42, title='An error occurred.')
            em.description = 'No results found.'
            return await ctx.send(embed=em)
        if len(res) > 2048:
            desc = self.utils.slice_text(res, 1900, f"...\n\nToo much! Read the rest at https://wikipedia.org/wiki/{query.replace(' ', '_')}")
            em.description = desc
        else:
            em.description = res
        em.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command(name='ascii')
    async def ascii_(self, ctx, *, text):
        """Send fancy ASCII text!"""
        resp = await self.session.get(f"http://artii.herokuapp.com/make?text={urllib.parse.quote_plus(text)}") 
        message = await resp.text()
        if len(f"```{message}```") > 2000:
            return await ctx.send('Your ASCII is too long!')
        await ctx.send(f"```{message}```")


    @commands.command(aliases=['semoji', 'searchem'])
    async def searchemoji(self, ctx, *, emoji):
        """Searches an emoji from the bot's servers."""
        await ctx.message.delete()
        e = discord.utils.get(self.bot.emojis, name=emoji)
        if e is None:
            return await ctx.send("No emoji found from the list of my servers.\nThe bot cannot search YOUR servers, only the servers that it is currently in.")
        resp = await self.session.get(f"https://cdn.discordapp.com/emojis/{e.id}") 
        resp = await resp.read()
        if e.animated:
            extension = '.gif'
        else:
            extension = '.png'
        await ctx.send(file=discord.File(resp, f"{e.name}{extension}"))

    @commands.command(aliases=['copyemoji', 'emojiadd', 'eadd', 'cemoji'])
    @commands.guild_only()
    @commands.has_permissions(manage_emojis = True)
    async def addemoji(self, ctx, *, emoji):
        """Adds an emoji by the emoji's name."""
        e = discord.utils.get(self.bot.emojis, name=emoji)
        if e is None:
            return await ctx.send("No emoji found from the list of my servers, with the given ID.")
            # await ctx.send("No emoji found from the list of my servers.\nYou can reply with an emoji ID, and the bot will add it for you. Otherwise, reply 'cancel' to end the search.")
            # try:
            #     x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=45.0)
            # except asyncio.TimeoutError:
            #     return await ctx.send("The request timed out. Please try again.")
            # if x.content.lower() == 'cancel':
            #     return await ctx.send("The process has ended.")
            # if self.bot.get_emoji(int(x.content)) is None:
            #     return await ctx.send("Sorry, no emoji with that ID is found. ¯\_(ツ)_/¯")
            # e = self.bot.get_emoji(int(x.content)) 
        count = 0
        animate = 0
        for x in ctx.guild.emojis:
            if not e.animated:
                if not x.animated:
                    count += 1
                else:
                    animate += 1
        if count >= 50 or animate >= 50:
            return await ctx.send(f"This server has reached the limit for custom emojis! {self.bot.get_emoji(430853757350445077)}")
        resp = await self.session.get(f"https://cdn.discordapp.com/emojis/{e.id}")
        img = await resp.read()
        try:
            em = discord.Embed(color=0xf9e236, title=f"The emoji has been created in the server! Name: {e.name}")
            await ctx.guild.create_custom_emoji(name=e.name, image=img)
            em.set_image(url=f"https://cdn.discordapp.com/emojis/{e.id}")
            await ctx.send(embed=em)
        except discord.Forbidden:
            return await ctx.send("The bot does not have Manage Emojis permission.")


    @commands.command(aliases=['daemojis', 'demojis'])
    @commands.guild_only()
    @commands.has_permissions(manage_emojis = True)
    async def deleteallemojis(self, ctx):
        """Deletes ALL emojis from your server."""
        await ctx.send("Note that this will remove all current emojis from the server. Continue? (Y/N)")
        x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
        if x.content.lower() == 'y' or x.content.lower() == 'yes':
            msg = await ctx.send("Deleting all emojis...")
            for x in ctx.guild.emojis:
                await x.delete()
            return await msg.edit(content='All emojis have been removed.')
        elif x.content.lower() == 'n' or x.content.lower() == 'no':
            return await ctx.send("Process cancelled.")
        else:
            return await ctx.send("Invalid response.")


    @commands.command(aliases=['addedefault', 'defaultemojis', 'default'])
    @commands.guild_only()
    @commands.has_permissions(manage_emojis = True)
    async def adddefaultemojis(self, ctx):
        """Add emojis to your server from a list of my default ones!"""
        if len(ctx.guild.emojis) > 0:
            # await ctx.send("Note that this will remove all current emojis from the server. Continue? (Y/N)")
            # x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
            # if x.content.lower() == 'y' or x.content.lower() == 'yes':
            #     msg = await ctx.send("Adding AWESOME emojis to your server!")
            #     for x in ctx.guild.emojis:
            #         await x.delete()
            # elif x.content.lower() == 'n' or x.content.lower() == 'no':
            #     return await ctx.send("Process cancelled.")
            # else:
            #     return await ctx.send("Invalid response.")
            return await ctx.send("The server must have NO emojis. To do these, run *deleteallemojis.")
        msg = await ctx.send("Adding emojis of GREATNESS to your server! These are hand picked by the legendary emoji god **dat banana boi**.")
        emojis = [430847504465133568, 430847552951156748, 430847565999636480, 430847578360250371, 430847593439035392, 430847606667870239, 430847624653045761, 430847640033296384, 430847651525951489, 430847673017434125, 430847716516691988, 430847743867617283, 430847838508023810, 430847922632917012, 430847963955331073, 430847990299885588, 430848003180462114, 430848018481152000, 430848034948120577, 430848052681637888, 430848071329382411, 430848115566706690, 430848132667146251, 430848267279138836, 430848283242528789, 430848300665667584, 430848314942947328, 430848332861276181, 430848350871355412, 430848366235353088, 430850475726995466, 430850499315499008, 430850522501611520, 430850541959118880,
                  430850576981688320, 430850608405413918, 430850635206885385, 430850660330635285, 430850708711931914, 430850742534930433, 430850840002166784, 430850866547785738, 430850929797890068, 430851443101270036, 430851505592205312, 430851860514209813, 430851871872253983, 430851935864881152, 430851951740321793, 430851991275569178, 430852387461398528, 430852409380700160, 430852484978835458, 430853515217469451, 430853554572361738, 430853629570711562, 430853641117630464, 430853676735791124, 430853687754358788, 430853698286256128, 430853715059277863, 430853728405291009, 430853744398303243, 430853757350445077, 430853771594170378, 430867679281283102, 430893757949280264, 436342184330002442]
        try:
            for x in emojis:
                e = self.bot.get_emoji(x)
                resp = await self.session.get(e.url)
                img = await resp.read()
                await ctx.guild.create_custom_emoji(name=e.name, image=img)
            await msg.edit(content="Done! Enjoy dat banana boi's collection of dank emojis. :white_check_mark:")
        except discord.Forbidden:
            return await msg.edit(content="Bot does not have Manage Emojis permission. :x:")




    
       

    @commands.command(aliases=['fb']) # lol fb
    @commands.guild_only()
    async def feedback(self, ctx, *, feedback=None):
        """How do YOU want this bot to be? Give your word here."""
        if feedback is None:
            color = 0xf44e42
            em = discord.Embed(color=color, title='Error :x:')
            em.description = 'Please enter your feedback.'
            await ctx.send(embed=em)
        else:
            try:
                lol = self.bot.get_channel(413814935391567882)
                color = 0xf9e236
                em = discord.Embed(color=color, title='Feedback')
                em.description = feedback
                em.set_author(name=f"Sent by: {ctx.author.name}", icon_url=ctx.author.avatar_url)
                em.set_footer(text=f"Sent from {ctx.guild.name} in #{ctx.channel.name}", icon_url=ctx.guild.icon_url)
                await lol.send(embed=em)
                em.description = 'Thanks for sending feedback to make this bot better! :ok_hand:'
                await ctx.send(embed=em)
            except Exception as e:
                color = 0xf44e42
                em = discord.Embed(color=color, title='Error :x:')
                em.description = f"More details: \n\n{e}"
                await ctx.send(embed=em)


    @commands.command(aliases=['hb'])
    async def hastebin(self, ctx, *, text):
        """Put some code in hastebin"""
        try:
            resp = await self.session.post("https://hastebin.com/documents", data=text)
            resp = await resp.json()
            color = 0xf9e236
            em = discord.Embed(color=color, title='Hastebin-ified!')
            em.description = f"Your Hastebin link: \nhttps://hastebin.com/{resp['key']}"
            em.set_footer(text=f"Created by: {ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)
        except Exception as e:
            color = 0xf44e42
            em = discord.Embed(color=color, title='An error occured. :x:')
            em.description = f"More details: \n```{e}```"
            await ctx.send(embed=em)


    @commands.command(aliases=['surl'])
    async def shortenurl(self, ctx, *, url):
        '''Shortens a URL through Tinyurl.'''
        color = 0xf9e236
        em = discord.Embed(color=color, title='TinyURL Link Shortener')
        resp = await self.session.get(f'http://tinyurl.com/api-create.php?url={url}')
        resp = await resp.text()
        em.description = f"Shortened Link: \n{resp}"
        em.add_field(name='Original Link', value=url)
        await ctx.send(embed=em)


    @commands.command()
    async def urban(self, ctx, *, word):
        '''Gets the definition of a word from Urban Dictionary.'''
        if not ctx.channel.nsfw:
            em = discord.Embed(color=0xf44242, title="Urban Dictionary only works in NSFW channels now.")
            em.description = "Why? Discord ToS limits any NSFW pictures **or words** to NSFW channels. Therefore, if Urban Dictionary shows NSFW words in any channel, that could violate ToS.\n\n**Please try this command in a NSFW channel.**"
            return await ctx.send(embed=em)
        resp = await self.session.get(f'http://api.urbandictionary.com/v0/define?term={word}')
        r = await resp.json()
        lol = []
        for x in r['list']:
            lol.append(f"{x['definition']} \n\n*{x['example']}* \n\n**Votes**\n:thumbsup: {x['thumbs_up']}  :thumbsdown: {x['thumbs_down']} \n\nDefinition written by {x['author']}")
        if not lol:
            return await ctx.send("Nope. No definitions found with this word.")
        ud = Pages(ctx, entries=lol, per_page=1)
        await ud.paginate()


    @commands.command()
    async def playing(self, ctx, *, game):
        '''Enter a game, and it will find users in the server that are playing it.'''
        msg = ""
        members = [x for x in ctx.guild.members if str(x.activity) == game]
        for x in members:
            msg += f"{str(x)} \n"
        if msg == "":
            msg = 'No one in the server is currently playing this game!'
        color = 0xf9e236
        em = discord.Embed(color=color, title=f"Users Playing: {game}")
        em.description = msg
        await ctx.send(embed=em) 
        
        
    @commands.command()
    async def ranint(self, ctx, a: int = None, b: int = None):
        """Usage: *ranint [least number][greatest number]. RanDOM!"""
        if a is None:
            await ctx.send("Boi, are you random! Usage: *ranint [least #] [greatest #], to set the range of the randomized number. Please use integers.")
        if b is None:
            await ctx.send("Boi, are you random! Usage: *ranint [least #] [greatest #], to set the range of the randomized number. Please use integers.")
        else:
            color = 0xf9e236
            em = discord.Embed(color=color, title='Your randomized number:')
            em.description = random.randint(a,b)
            await ctx.send(embed=em)
            
                    
    @commands.command()
    async def rolldice(self, ctx):
        """Rolls a 6 sided die."""
        choices = ['1', '2', '3', '4', '5', '6']
        color = 0xf9e236
        em = discord.Embed(color=color, title='Rolled! (1 6-sided die)', description=random.choice(choices))
        await ctx.send(embed=em)
        

    @commands.command()
    async def flipcoin(self, ctx):
        """Flip a coin. Any coin."""
        choices = ['Heads', 'Tails', 'Coin self-destructed.', '¯\_(ツ)_/¯']
        color = 0xf9e236
        em=discord.Embed(color=color, title='Flipped a coin!')
        em.description = random.choice(choices)
        await ctx.send(embed=em)


    @commands.command()
    async def choose(self, ctx, *, args):
        """Can't choose. Let this bot do it for you. Seperate choices with a comma."""
        lol = self.bot.get_emoji(453323541639725079)
        msg = await ctx.send(lol)
        args = args.split(",")
        await asyncio.sleep(2)
        res = await commands.clean_content().convert(ctx, random.choice(args).strip(" "))
        await msg.edit(content=f"Alright! I choose:\n**{res}**")

        
    @commands.command(aliases=['tf'])
    async def textface(self, ctx, Type):
        """Get those dank/cool faces here. Type *textface list for a list."""
        if Type.lower() == 'lenny':
          await ctx.send('( ͡° ͜ʖ ͡°)')
        elif Type.lower() == 'tableflip':
          await ctx.send('(ノಠ益ಠ)ノ彡┻━┻')
        elif Type.lower() == 'shrug':
          await ctx.send('¯\_(ツ)_/¯')
        elif Type.lower() == 'bignose':
          await ctx.send('(͡ ͡° ͜ つ ͡͡°)')
        elif Type.lower() == 'iwant':
          await ctx.send('ლ(´ڡ`ლ)')
        elif Type.lower() == 'musicdude':
          await ctx.send('ヾ⌐*_*ノ♪')
        elif Type.lower() == 'wot':
          await ctx.send('ლ,ᔑ•ﺪ͟͠•ᔐ.ლ')
        elif Type.lower() == 'bomb':
          await ctx.send('(´・ω・)っ由')
        elif Type.lower() == 'orlly':
          await ctx.send("﴾͡๏̯͡๏﴿ O'RLY?")
        elif Type.lower() == 'money':
          await ctx.send('[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]')
        elif Type.lower() == 'list':
          color = 0x00ff00
          em = discord.Embed(color=color, title='List of Textfaces')
          em.description = 'Choose from the following: lenny, tableflip, shrug, bignose, iwant, musicdude, wot, bomb, orlly, money. Type *textface [face].'
          em.set_footer(text="Don't you dare question my names for the textfaces.")
          await ctx.send(embed=em)
        else:
          await ctx.send('That is NOT one of the dank textfaces in here yet. Use *textface list to see a list of the textfaces.')
            
            
    @commands.command(aliases=['av'])
    async def avatar(self, ctx, user: discord.Member = None):
        """Returns a user's avatar url. Use *av [user], or just *av for your own."""
        if user is None:
            av = ctx.message.author.avatar_url
            if '.gif' in av:
                av += "&f=.gif"
            color = 0xf9e236
            em = discord.Embed(color=color, title=ctx.message.author.name)
            em.set_author(name='Profile Picture')
            em.set_image(url=av)
            await ctx.send(embed=em)                  
        else:
            av = user.avatar_url
            if '.gif' in av:
                av += "&f=.gif"
            color = 0x00ff00
            em = discord.Embed(color=color, title=user.name)
            em.set_author(name='Profile Picture')
            em.set_image(url=av)
            await ctx.send(embed=em)
            
            
    @commands.command(aliases=['ui'])
    async def userinfo(self, ctx, user: discord.Member = None):
        """Dig out that user info. Usage: *userinfo [tag user]"""
        if user is None:
            user = ctx.author
        join_time = str(ctx.author.joined_at.strftime("%A, %b %d, %Y, at %I:%M %p"))
        status = {
            "online": f"{self.bot.get_emoji(522530301793009665)} Online",
            "idle": f"{self.bot.get_emoji(522530301759455238)} Idle",
            "dnd": f"{self.bot.get_emoji(522530301503864854)} Do Not Disturb",
            "offline": f"{self.bot.get_emoji(522530301617111062)} Offline"
        }
        color = 0xf2f760
        em = discord.Embed(color=color, title=f'User Info: {str(user)}')
        em.add_field(name="User Stats", value="-", inline=False)
        em.add_field(name='Status', value=status[str(user.status)])       
        em.add_field(name='Account Created', value=user.created_at.__format__('%A, %B %d, %Y'))
        em.add_field(name='ID', value=f'{user.id}')
        Type = 'Bot' if user.bot else 'Human'
        em.add_field(name='Profile Type', value=Type)
        em.add_field(name='Currently Playing', value=user.activity.name if user.activity else 'Not playing anything!')
        em.add_field(name="User Stats in Server", value=user.guild.name, inline=False)
        em.add_field(name="Total Roles", value=len(ctx.author.roles))
        em.add_field(name="Top Role", value=user.top_role)
        em.add_field(name="Nickname", value=user.nick or "No Nickname")
        em.add_field(name="Join Time", value=join_time)
        em.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=em)  
        
              
    @commands.command(aliases=['si'])
    async def serverinfo(self, ctx, *, guild_name = None):
        """Are you a nerd? Here's some server info."""
        guild = None
        if not guild_name:
            guild = ctx.guild
        else:
            for g in self.bot.guilds:
                if g.name.lower() == guild_name.lower():
                    guild = g
                    break
                if str(g.id) == str(guild_name):
                    guild = g
                    break
        if not guild:
            await ctx.send("Oof. I couldn't find that guild...\nThe bot can only search from the servers it is in.")
            return
        roles = [x.name for x in guild.roles]
        role_length = len(roles)
        roles = ', '.join(roles)
        textchannels = len(guild.text_channels)
        voicechannels = len(guild.voice_channels)
        time = str(guild.created_at.strftime("%b %d, %Y, %A, %I:%M %p"))
        try:
            ban_count = len(await guild.bans())
        except discord.Forbidden:
            ban_count = "Could not retrieve bans (I need Ban Members permission)"
        verification_levels = {
            0: "**None** (Unrestricted)",
            1: "**Low** (Verified email)",
            2: "**Medium** (Registered on Discord for longer than 5 minutes)",
            3: "**(╯°□°）╯︵ ┻━┻** (Registered on Discord for longer than 10 minutes)",
            4: "**(ノಠ益ಠ)ノ彡┻━┻** (Verified phone)"
        }         
        content_filters = {
            0: "**None** (Don't scan any messages.)",
            1: "**Medium** (Scan messages from members without a role.)",
            2: "**High** (Scan messages sent by all members.)"
        }
        mfa_levels = {
            0: "Does not require 2FA for members with Administrator permission.",
            1: "Requires 2FA for members with Administrator permission."
        }
        regular_emojis = len([x for x in guild.emojis if not x.animated])
        animated_emojis = len([x for x in guild.emojis if x.animated])
        # online_members = 0
        # bot_member     = 0
        # bot_online     = 0
        # for member in guild.members:
        #     if member.bot:
        #         bot_member += 1
        #         if not member.status == discord.Status.offline:
        #                 bot_online += 1
        #         continue
        #     if not member.status == discord.Status.offline:
        #         online_members += 1
        # # bot_percent = "{:,g}%".format((bot_member/len(guild.members))*100)
        # user_string = "{:,}/{:,} online ({:,g}%)".format(
        #     online_members,
        #     len(guild.members) - bot_member,
        #     round((online_members/(len(guild.members) - bot_member) * 100), 2)
        # )
        # b_string = "bot" if bot_member == 1 else "bots"
        # user_string += "\n{:,}/{:,} {} online ({:,g}%)".format(
        #     bot_online,
        #     bot_member,
        #     b_string,
        #     round((bot_online/bot_member)*100, 2)
        # )
        regular_emoji_list = " ".join(str(self.bot.get_emoji(x.id)) for x in guild.emojis if not x.animated)
        animated_emoji_list = " ".join(str(self.bot.get_emoji(x.id)) for x in guild.emojis if x.animated)
        em = discord.Embed(title=guild.name, colour = ctx.author.color)
        em.set_thumbnail(url=guild.icon_url)
        em.add_field(name='Server ID :id:', value=str(guild.id), inline=False)
        em.add_field(name=f'Owner {self.bot.get_emoji(430340802879946773)}', value=str(guild.owner), inline=False)
        # em.add_field(name='Members ({;,} total)'.format(len(guild.members)), value=user_string)
        em.add_field(name='Total Member Count :busts_in_silhouette:', value=str(guild.member_count), inline=False) 
        em.add_field(name='Humans :family:', value=len([x for x in guild.members if not x.bot]), inline=False) 
        em.add_field(name='Bots :robot:', value=len([x for x in guild.members if x.bot]), inline=False) 
        em.add_field(name='Category Count :page_facing_up:', value=len(guild.categories), inline=False)
        em.add_field(name='Channel Count :speech_balloon:  ', value=f":hash: **Text:** {textchannels}\n:loud_sound: **Voice:** {voicechannels}", inline=False)
        em.add_field(name='AFK Channel :sleeping: ', value=f"**Channel**: {str(guild.afk_channel)}\n**Timeout:** {int(guild.afk_timeout / 60)} minutes", inline=False)
        em.add_field(name='Server Region :globe_with_meridians: ', value=str(guild.region), inline=False)
        em.add_field(name=f'Emoji Count {self.bot.get_emoji(484366851493855233)}', value=f"**Regular Emojis:** {regular_emojis}\n**Animated Emojis:** {animated_emojis}", inline=False)
        em.add_field(name='Role Count :bust_in_silhouette: ', value=str(role_length), inline=False)
        em.add_field(name=f'Server Verification Level {self.bot.get_emoji(522927676114075649)}', value=verification_levels[guild.verification_level], inline=False)
        em.add_field(name=f"Explicit Content Filter {self.bot.get_emoji(464784851241926666)}", value=content_filters[guild.explicit_content_filter], inline=False)
        em.add_field(name=f"2FA Requirement {self.bot.get_emoji(485798151064649749)}", value=mfa_levels[guild.mfa_level], inline=False)
        em.add_field(name=f'Ban Count {self.bot.get_emoji(522534996666220546)}', value=ban_count, inline=False)
        # em.add_field(name="Regular Emojis", value=regular_emoji_list, inline=False)
        # em.add_field(name="animated Emojis", value=animated_emoji_list, inline=False)
        em.set_footer(text='Created - %s' % time)        
        await ctx.send(embed=em)
              

    @commands.command(aliases=['rinfo'])
    @commands.guild_only()
    async def roleinfo(self, ctx, *, rolename):
        try:
            role = discord.utils.get(ctx.guild.roles, name=rolename)
        except:
            return await ctx.send("Role not found. Please make sure the role name is correct. (Case Sensitive!)")
        em = discord.Embed(color=role.color, title=f'Role Info: {rolename}')
        p = ""
        if role.permissions.administrator:
            p += "Administrator :white_check_mark: \n"
        else:
            p += "Administrator :x: \n"
        if role.permissions.create_instant_invite:
            p += "Create Instant Invite :white_check_mark: \n"
        else:
            p += "Create Instant Invite :x:\n"
        if role.permissions.kick_members:
            p += "Kick Members :white_check_mark: \n"
        else:
            p += "Kick Members :x:\n"
        if role.permissions.ban_members:
            p += "Ban Members :white_check_mark: \n"
        else:
            p += "Ban Members :x:\n"
        if role.permissions.manage_channels:
            p += "Manage Channels :white_check_mark: \n"
        else:
            p += "Manage Channels :x:\n"
        if role.permissions.manage_guild:
            p += "Manage Server :white_check_mark: \n"
        else:
            p += "Manage Server :x:\n"
        if role.permissions.add_reactions:
            p += "Add Reactions :white_check_mark: \n"
        else:
            p += "Add Reactions :x:\n"
        if role.permissions.view_audit_log:
            p += "View Audit Log :white_check_mark: \n"
        else:
            p += "View Audit Log :x:\n"
        if role.permissions.read_messages:
            p += "Read Messages :white_check_mark: \n"
        else:
            p += "Read Messages :x:\n"
        if role.permissions.send_messages:
            p += "Send Messages :white_check_mark: \n"
        else:
            p += "Send Messages :x:\n"
        if role.permissions.send_tts_messages:
            p += "Send TTS Messages :white_check_mark: \n"
        else:
            p += "Send TTS Messages :x:\n"
        if role.permissions.manage_messages:
            p += "Manage Messages :white_check_mark: \n"
        else:
            p += "Manage Messages :x:\n"
        if role.permissions.embed_links:
            p += "Embed Links :white_check_mark: \n"
        else:
            p += "Embed Links :x:\n"
        if role.permissions.attach_files:
            p += "Attach Files :white_check_mark: \n"
        else:
            p += "Attach Files \n" 
        if role.permissions.read_message_history:
            p += "Read Message History :white_check_mark: \n"
        else:
            p += "Read Message History :x:\n"
        if role.permissions.mention_everyone:
            p += "Mention @everyone :white_check_mark: \n"
        else:
            p += "Mention @everyone :x:\n"
        if role.permissions.external_emojis:
            p += "Use External Emojis :white_check_mark: \n"
        else:
            p += "Use External Emojis :x:\n"
        if role.permissions.change_nickname:
            p += "Change Nicknames :white_check_mark: \n"
        else:
            p += "Change Nicknames :x:\n"
        if role.permissions.manage_nicknames:
            p += "Manage Nicknames :white_check_mark: \n"
        else:
            p += "Manage Nicknames :x:\n"
        if role.permissions.manage_roles:
            p += "Manage Roles :white_check_mark: \n"
        else:
            p += "Manage Roles :x:\n"
        if role.permissions.manage_webhooks:
            p += "Manage Webhooks :white_check_mark: \n"
        else:
            p += "Manage Webhooks :x:\n"
        if role.permissions.manage_emojis:
            p += "Manage Emojis :white_check_mark: \n"
        else:
            p += "Manage Emojis :x:\n"
        v = "" 
        if role.permissions.connect:
            v += "Connect :white_check_mark: \n"
        else:
            v += "Connect :x:\n"
        if role.permissions.speak:
            v += "Speak :white_check_mark: \n"
        else:
            v += "Speak :x:\n"
        if role.permissions.mute_members:
            v += "Mute Members :white_check_mark: \n"
        else:
            v += "Mute Members :x:\n"
        if role.permissions.deafen_members:
            v += "Deafen Members :white_check_mark: \n"
        else:
            v += "Deafen Members :x:\n"
        if role.permissions.move_members:
            v += "Move Members :white_check_mark: \n"
        else:
            v += "Move Members :x:\n"
        if role.permissions.use_voice_activation:
            v += "Use Voice Activation :white_check_mark: \n"
        else:
            v += "Use Voice Activation :x:\n"
        em.description = f"**General Permissions** \n\n{p} \n\n\n**Voice Permissions** \n\n{v}"
        em.add_field(name='ID', value=role.id)
        em.add_field(name='Position from Bottom', value=role.position)
        if role.mentionable:
            a = 'Mentionable'
        else:
            a = 'Not Mentionable'
        em.add_field(name='Mentionable', value=a)
        em.add_field(name='Time Created', value=str(role.created_at.strftime("%A, %b %m, %Y at %I:%M %p")))
        # member = ""
        # for x in role.members:
        #     member += f"{x.name} \n"
        # em.add_field(name='Members in the Role', value=member)
        await ctx.send(embed=em)





def setup(bot): 
    bot.add_cog(Utility(bot))               
