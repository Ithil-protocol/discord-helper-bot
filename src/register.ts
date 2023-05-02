// discord commands must be registered via their API before being used

import { env } from '@/config'
import { REST, Routes, SlashCommandBuilder } from 'discord.js'

const commands = [
  new SlashCommandBuilder().setName('ping').setDescription('Replies with Pong!'),
  new SlashCommandBuilder()
    .setName('fund_eth')
    .setDescription('Funds the provided wallet with ETH.')
    .addStringOption((option) => option.setName('wallet').setDescription('The wallet to fund.').setRequired(true)),
].map((command) => command.toJSON())

console.log(commands)

const rest = new REST({ version: '10' }).setToken(env.DISCORD_TOKEN)

const main = async () => {
  try {
    console.log('Started refreshing application (/) commands.')

    await rest.put(Routes.applicationCommands(env.DISCORD_APP_ID), { body: commands })

    console.log('Successfully reloaded application (/) commands.')
  } catch (error) {
    console.error(error)
  }
}

void main()
