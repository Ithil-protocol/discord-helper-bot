import os
from discord import utils, Game
from discord.ext import commands
import time
import requests
import logging
import configparser
from typing import Dict
from argparse import ArgumentParser
from discord_bot.webserver import Webserver
from discord_bot.transaction_manager import TransactionManager


logging.basicConfig(
    format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p", level=logging.INFO
)


def _setup_transaction_manager(config) -> TransactionManager:
    infura_key = _get_from_config_or_env_var(config, "API", "INFURA_KEY")
    network = _get_from_config_or_env_var(config, "DEFAULT", "NETWORK")
    private_key = _get_from_config_or_env_var(config, "USER", "PRIVATE_KEY")
    eth_amount = _get_from_config_or_env_var(config, "DEFAULT", "SEND_ETH_AMOUNT")

    return TransactionManager(
        infura_key=infura_key,
        network=network,
        private_key=private_key,
        amount=eth_amount
    )


def _get_from_config_or_env_var(
        config: Dict,
        section: str,
        key: str,
    ) -> str:
    value = config[section][key]
    if value == "":
        value = os.environ[key]

    return value


def _init_userlist(config) -> Dict[str, int]:
    public_key = _get_from_config_or_env_var(config, "USER", "PUBLIC_KEY")
    etherscan_api_key = _get_from_config_or_env_var(config, "API", "ETHERSCAN_KEY")

    url = ("https://api-goerli.etherscan.io/api?module=account&action=txlist&address="+public_key+"&startblock=0&endblock=999999999&sort=asc&apikey"+etherscan_api_key)
    r = requests.get(url)
    transactions = r.json()
    if(transactions['message'] == 'NOTOX'):
        logging.error("Throttling Error")
        exit(1)

    userlist = {}
    for tx in transactions['result']:
        if(tx['gas'] == "21000" and tx['from'] == public_key.lower()):
            userlist[tx['to']] = tx['timeStamp']

    return userlist


def run_app():
    parser = ArgumentParser()
    parser.add_argument(
        "configfile", metavar="configfile", type=str, help="The bot configuration file"
    )
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.configfile)

    transaction_manager = _setup_transaction_manager(config)
    userlist = _init_userlist(config)
    news_channel = int(_get_from_config_or_env_var(config, "API", "DISCORD_NEWS_CHANNEL"))
    discord_key = _get_from_config_or_env_var(config, "API", "DISCORD_KEY")

    bot = commands.Bot(command_prefix='/', help_command=None)

    @bot.event
    async def on_ready():
        game = Game("with magic")
        await bot.change_presence(activity=game)
        channel = bot.get_channel(news_channel)
        await channel.send(f'{bot.user} has connected to the server!')


    @bot.event
    async def on_disconnect():
        channel = bot.get_channel(news_channel)
        await channel.send(f'{bot.user} has disconnected from the server!')


    @bot.command(name='help', help='Shows the help resource')
    @commands.has_any_role('Apprentices', 'Mods', 'Marketing Wiz', 'Core Team')
    async def help(ctx):
        await ctx.send('Summary of available commands:\n- `/help` shows this help message\n- `/resource [langing, app, docs, blog, twitter]` shows the relevant resource\n- `/fund 0xabc...` sends 0.02 gETH (Goerli test ETH) to the specified wallet **only once per wallet!**')


    @bot.command(name='resource', help='Show the link to a resource', usage='landing, app, docs, blog, twitter')
    @commands.has_any_role('Apprentices', 'Mods', 'Marketing Wiz', 'Core Team')
    async def resource(ctx, resource: str):
        if resource == 'landing':
            await ctx.send('Here you have:\nhttps://ithil.fi')
        elif resource == 'app':
            await ctx.send('Here you have:\nhttps://app.ithil.fi')
        elif resource == 'docs':
            await ctx.send('Here you have:\nhttps://docs.ithil.fi')
        elif resource == 'blog':
            await ctx.send('Here you have:\nhttps://ithil-protocol.medium.com')
        elif resource == 'twitter':
            await ctx.send('Here you have:\nhttps://twitter.com/ithil_protocol')
        else:
            await ctx.send('Invalid resource selected')

    @bot.command(name='fund', help='Send the wallet 0.02 gETH', usage='0x123...')
    @commands.has_any_role('Apprentices', 'Mods', 'Marketing Wiz', 'Core Team')
    async def fund(ctx, wallet: str):
        if(
            wallet == '0x000000000000000000000000000000000000dEaD' or wallet == '0x0000000000000000000000000000000000000000'
        ):
            await ctx.send('Cannot send to null address')
        elif not transaction_manager.is_valid(wallet):
            await ctx.send('Invalid address provided')
        elif(transaction_manager.balance() <= 100000000000000000):
            await ctx.send('Not enough gETH, retry in a while')
        else:
            try:
                q = userlist[wallet.lower()]
            except:
                txid = transaction_manager.send_eth(wallet)
                if(txid != None):
                    userlist[wallet.lower()] = int(time.time())
                    response = 'Funded!'
                    await ctx.send(response)
            else:
                await ctx.send('Already claimed funds')

    @bot.event
    async def on_command_error(ctx, error):    
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.MissingRole):
            await ctx.send(error)
        elif isinstance(error, commands.BadArgument):
            usage = f'{bot.command_prefix}{ctx.command.name} {ctx.command.usage}'
            await ctx.send('Incorrect command argument\nCorrect usage: `{usage}`')
        else:
            logging.error(str(error))

    ws = Webserver(bot, userlist)
    bot.add_cog(ws)
    bot.loop.create_task(ws.webserver())
    bot.run(discord_key)
