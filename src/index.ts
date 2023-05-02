import { handleCommand } from './commands/fund_eth.command'
import { env } from '@/config'
import { Client, type CommandInteraction, GatewayIntentBits } from 'discord.js'

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages] })

client.on('ready', () => {
  console.log(`Logged in as ${client.user?.tag}!`)
})

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isCommand()) return
  const commandInteraction = interaction as CommandInteraction
  const { commandName } = commandInteraction

  if (commandName === 'ping') {
    await commandInteraction.reply('Pong!')
  }

  if (commandName === 'fund_eth') return await handleCommand(commandInteraction)
})

void client.login(env.DISCORD_TOKEN)
