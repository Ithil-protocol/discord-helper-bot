# bot.py
import os
from discord import utils, Game
from discord.ext import commands
from dotenv import load_dotenv
from web3 import Web3
from tinydb import TinyDB, Query
import time

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
INFURA_API_KEY = os.getenv('INFURA_API_KEY')
PUBLIC_KEY = os.getenv('PUBLIC_KEY')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
DB_NAME = os.getenv('DB_NAME')
NEWS_CHANNEL = int(os.getenv('NEWS_CHANNEL'))

bot = commands.Bot(command_prefix='$')
w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/'+INFURA_API_KEY))
db = TinyDB(DB_NAME)

@bot.event
async def on_ready():
    game = Game("with magic")
    await bot.change_presence(activity=game)
    channel = bot.get_channel(NEWS_CHANNEL)
    await channel.send(f'{bot.user} has connected to the server!')

@bot.event
async def on_disconnect():
    channel = bot.get_channel(NEWS_CHANNEL)
    await channel.send(f'{bot.user} has disconnected from the server!')

@bot.command(name='resource', help='Show the link to a resource', usage='landing, app, docs, blog, twitter')
@commands.has_role('Mods')
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

@bot.command(name='fund', help='Send the wallet 0.1 gETH', usage='0x123...')
@commands.has_role('Managers')
async def fund(ctx, wallet: str):
    if(
        wallet == '0x000000000000000000000000000000000000dEaD' or
        wallet == '0x0000000000000000000000000000000000000000'
    ):
        await ctx.send('Cannot send to null address')
    elif not w3.isAddress(wallet):
        await ctx.send('Invalid address provided')
    else:
        q = Query()
        table = db.table('requests')
        if not table.search(q.user == ctx.message.author.name):
            table.insert({
                'user': ctx.message.author.name, 
                'wallet': wallet,
                'timestamp': int(time.time())
            })
            tx = {
                'nonce': w3.eth.get_transaction_count(PUBLIC_KEY),
                'to': wallet,
                'value': w3.toWei(0.1, 'ether'),
                'gas': 21000,
                'gasPrice': w3.toWei('5', 'gwei')
            }

            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            response = 'Funded! https://goerli.etherscan.io/tx/'+w3.toHex(tx_hash)
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
        table = db.table('errors')
        table.insert({
            'error': str(error),
            'timestamp': int(time.time())
        })

bot.run(TOKEN)
