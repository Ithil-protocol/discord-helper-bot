import logging
import os
import json
from argparse import ArgumentParser
from configparser import ConfigParser
from typing import Dict
from pathlib import Path

from discord import Game, Intents, DMChannel, ChannelType
from discord.ext import commands

from discord_bot.transaction_manager import TransactionManager
from discord_bot.user_manager import UserManager
from discord_bot.helpers import helper_cmd, resource_cmd, send_eth_cmd, send_tokens_cmd

logging.basicConfig(
    format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p", level=logging.INFO
)

async def report_error(ctx, error_str):
    await ctx.send(error_str)
    logging.error(f"Error reported: " + error_str)


def _setup_transaction_manager(config) -> TransactionManager:
    rpc_url = _get_from_config_or_env_var(config, "CHAIN", "RPC_URL")
    private_key = _get_from_config_or_env_var(config, "CHAIN", "PRIVATE_KEY")
    eth_amount = _get_from_config_or_env_var(config, "DEFAULT", "SEND_ETH_AMOUNT")

    return TransactionManager(
        rpc_url=rpc_url,
        private_key=private_key,
        amount=float(eth_amount),
    )

def _setup_user_manager(config) -> UserManager:
    db_path = _get_from_config_or_env_var(config, "DEFAULT", "DB_PATH")
    throttle_time = _get_from_config_or_env_var(config, "DEFAULT", "THROTTLE_TIME")

    return UserManager(db_path, throttle_time)

def _setup_tokens_array(config):
    tokens = {}

    input_file = _get_from_config_or_env_var(config, "CHAIN", "TOKENS")

    # Load the input JSON from the file
    with open(input_file, "r") as f:
        input_json = f.read()

    # Parse the JSON string into a dictionary
    parsed_dict = json.loads(input_json)

    # Access and print values from the parsed dictionary dynamically
    for key, value in parsed_dict.items():
        tokens[key] = value

    return tokens

def _get_from_config_or_env_var(
    config: Dict,
    section: str,
    key: str,
) -> str:
    value = config[section][key]
    if value == "":
        value = os.environ[key]

    return value


async def create_thread(ctx: any):
    return await ctx.channel.create_thread(name="Talking with "+str(ctx.author) , type=ChannelType.public_thread )


def run_app() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "configfile", metavar="configfile", type=str, help="The bot configuration file"
    )
    args = parser.parse_args()

    config = ConfigParser()
    config.read(args.configfile)

    tokens = {}
    tokens = _setup_tokens_array(config)
    transaction_manager = _setup_transaction_manager(config)
    user_manager = _setup_user_manager(config)

    discord_key = _get_from_config_or_env_var(config, "DEFAULT", "DISCORD_KEY")
    data_path = Path(os.environ.get("DATA_DIR", os.getcwd()))
    if not data_path.exists():
        raise OSError(f"Data path {data_path} does not exist!")

    """
    Settings for the bot
    """
    bot = commands.Bot(intents=Intents.all(), command_prefix="/", help_command=None)


    @bot.event
    async def on_ready():
        game = Game("with magic")
        await bot.change_presence(activity=game)


    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(
            error, commands.MissingRole
        ):
            await ctx.send(error)
        elif isinstance(error, commands.BadArgument):
            usage = f"{bot.command_prefix}{ctx.command.name} {ctx.command.usage}"
            await ctx.send("Incorrect command argument\nCorrect usage: `{usage}`")
        else:
            await report_error(ctx, str(error))


    @bot.event
    async def on_message(message):
        if(message.author.id == bot.user.id):
            return
        elif isinstance(message.channel, DMChannel):
            msg = message.content.split()
            if(msg[0] == "send_eth"):
                if(len(msg) != 2):
                    await message.channel.send("Invalid command, use `send_eth YOUR_WALLET_ADDRESS`")
                    return

                await message.channel.send("Casting the spell...")
                await message.channel.send(send_eth_cmd(msg[1], user_manager, transaction_manager))
            elif(msg[0] == "send_tokens"):
                if(len(msg) != 3):
                    await message.channel.send("Invalid command, use `send_tokens YOUR_WALLET_ADDRESS TOKEN_NAME`")
                    return

                try:
                    token_data = tokens[msg[2]]
                except:
                    keys = []
                    for key, value in tokens.items():
                        keys.append(key)
                    await message.channel.send("Token not supported, please use one of the following " + str(keys))
                    return

                await message.channel.send("Casting the spell...")
                await message.channel.send((send_tokens_cmd(msg[1], token_data["address"], token_data["faucet"], user_manager, transaction_manager)))
            else:
                await message.channel.send("Invalid command, use `send_eth 0xabc...` or `send_tokens 0xabc... TKN_NAME`")
        else:
            await bot.process_commands(message)


    @bot.command(name="help", help="Shows the help resource")
    @commands.has_any_role("Ithilian")
    async def help(ctx):
        await ctx.reply(helper_cmd())


    @bot.command(
        name="resource",
        help="Show the link to a resource",
        usage="landing, dex, app, docs, blog, twitter",
    )
    @commands.has_any_role("Ithilian")
    async def resource(ctx, resource: str):
        await ctx.reply(resource_cmd(resource))


    @bot.command(name="send_eth", help="Send the wallet 0.02 ETH", usage="0x123...")
    @commands.has_any_role("Ithilian")
    async def send_eth(ctx, wallet: str) -> None:
        thread = await create_thread(ctx)

        await thread.send("Casting the spell...")
        await thread.send(send_eth_cmd(wallet, user_manager, transaction_manager))


    @bot.command(name="send_tokens", help="Send to a wallet 1000 tokens", usage="0x123... TKN_NAME")
    @commands.has_any_role("Ithilian")
    async def send_tokens(ctx, wallet: str, token: str) -> None:
        thread = await create_thread(ctx)

        try:
            token_data = tokens[token]
        except:
            keys = []
            for key, value in tokens.items():
                keys.append(key)
            await thread.send("Token not supported, please use one of the following " + str(keys))
            return

        await thread.send("Casting the spell...")
        await thread.send(send_tokens_cmd(wallet, token_data["address"], token_data["faucet"], user_manager, transaction_manager))


    @bot.command(name="statistics", hidden=True)
    @commands.has_any_role("Community Manager", "Mod", "Marketing Wiz", "Core Team")
    async def statistics(ctx) -> None:
        await ctx.reply(user_manager.dump_db())


    bot.run(discord_key)
