import json
from aiohttp import web
from typing import Dict
import asyncio
import discord 
from discord.ext import commands

class Webserver(commands.Cog):
    def __init__(self, bot, users: Dict[str, int]):
        self.bot = bot
        self.users = users

    async def webserver(self):
        async def handler(request):
            return web.Response(text="Hello, world")

        async def users_handler(request):
            return web.Response(text=json.dumps(self.users))

        app = web.Application()
        app.router.add_get('/', handler)
        app.router.add_get('/users', users_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        self.site = web.TCPSite(runner, '0.0.0.0', 8080)
        await self.bot.wait_until_ready()
        await self.site.start()

    def __unload(self):
        asyncio.ensure_future(self.site.stop())
