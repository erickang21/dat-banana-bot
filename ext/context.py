import asyncio
from discord.ext import commands
from cogs.utils.paginator import Pages

def resolve_code(content, code):
    """Helper to resolve codeblocks"""
    if type(code) == bool: # normal codeblock
        return f"```{content}```"
    if type(code) == str: # syntax codeblock
        return f"```{code}\n{content}```"
    raise Exception("Expected codeblock to be a boolean or string")

class DatContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def purge(self, limit):
        '''Shortcut to ctx.channel.purge'''
        return await self.channel.purge(limit=limit)
        
    @property
    def session(self):
        '''Returns bot session.'''
        return self.bot.session
    
    @property
    def db(self):
        '''Another shorter access to the database.'''
        return self.bot.db
        
    def page(self, text: str):
        '''Simple generator that paginates text.'''
        last = 0
        pages = []
        for curr in range(0, len(text)):
            if curr % 1980 == 0:
                pages.append(text[last:curr])
                last = curr
                appd_index = curr
        if appd_index != len(text) - 1:
            pages.append(text[last:curr])
        return list(filter(lambda a: a != '', pages))

    def paginate(self, entries, per_page=5):
        Pages(self, entries=entries, per_page=per_page)

    async def set_permissions(self, user, **permissions):
        await self.channel.set_permissions(user, **permissions)

    async def mute(self, user, time: int = None):
        await self.channel.set_permissions(user, send_messages=False)
        if time:
            await asyncio.sleep(time)
            await self.channel.set_permissions(user, send_messages=True)

    async def unmute(self, user):
        await self.channel.set_permissions(user, send_messages=True)

    async def _send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        """Sends messages with editing support
        don't call this directly, use Context#send
        this is just a helper method used by send
        """
        if file or files: # Can't edit attachments ¯\_(ツ)_/¯
            return await super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)
        msg = self.bot.edits.get(self.message.id)
        if msg:
            await msg.edit(content=content, embed=embed, delete_after=delete_after)
            return msg
        msg = await super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)
        if file or files: # Don't store messages with attachments
            return msg
        self.bot.edits[self.message.id] = msg
        return msg


    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None, code=None, split=False, edit=True):
        '''Custom send with extra functionality.'''
        if code and content:
            content = resolve_code(content, code)
        if split:
            x = self.page(content)
            for page in x:
                if page == x[-1]:
                    return await self.send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, edit=edit, code=code, split=split)
                    break
                else:
                    return await self.send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, edit=edit, code=code, split=split)
        if not edit:
            return await super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)
        return await self._send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)
            

    async def send_codeblock(self, content, lang=None):
        to_send = f"```{content}```" if not lang else f"```{lang}\n{content}```"
        return await super().send(to_send)

    async def get(self, url, headers={}, params={}, json=False):
        '''Easy method to request APIs etc.
        This method is for GET.
        Params:
        
        url (str): url to request to.
        headers (dict): Request headers if needed, optional
        params (dict): Request query string if needed.
        json (bool): Boolean if this request sends json.
        
        Example:
        resp = await ctx.get("http://cool-api.com", { "Authorization": "My secret key" }, json=True)
        print(resp['name'])
        '''
        try:
            resp = await self.session.get(url, headers=headers, params=params)
            if json:
                try:
                    return await resp.json()
                except Exception as e:
                    raise e
            else:
                return resp
        except Exception as e:
            raise e          
