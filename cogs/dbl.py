import json
import aiohttp
import asyncio
import os
uri = 'https://discordbots.org/api'

class dbl:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def __unload(self):
        self.bot.loop.create_task(self.session.close())

    async def send(self):
        dump = json.dumps({
            'server_count': len(self.bot.guilds)
        })
        head = {
            'authorization': os.environ.get('DBLTOKEN'), #idk what to do with aws
            'content-type' : 'application/json'
        }

        url = '{0}/bots/3884763367774617708/stats'.format(uri)

        async with self.session.post(url, data=dump, headers=head) as resp:
            print('returned {0.status} for {1} on dbl'.format(resp, dump))

    async def on_guild_join(self, server):
        await self.send()

    async def on_guild_remove(self, server):
        await self.send()

    async def on_ready(self):
        await self.send()
        
        
    
        

def setup(bot):
    bot.add_cog(dbl(bot))
