from discord.ext import commands
#
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
        return self.bot.db.datbananabot
        
    def paginate(text: str):
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
        
    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None, code=None, split=False):
        '''Custom send with extra functionality.'''
        if code and content:
            if type(code) == bool:
                content = f"```{content}```"
            else:
                content = f"```{code}\n{content}```"
        if split:
            x = self.paginate(content)
            for page in x:
                if page == x[-1]:
                    super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)
                    break
                else:
                    super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)
        else:
            super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)
            
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
            async with self.session.get(url, headers=headers, params=params) as resp:
                if json:
                    try:
                        return await resp.json()
                    except Exception as e:
                        raise e
                else:
                    return resp
        except Exception as e:
            raise e          