import { env } from './config'
import { Client, type CommandInteraction, GatewayIntentBits } from 'discord.js'

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages] })

client.on('ready', () => {
  console.log(`Logged in as ${client.user?.tag}!`)
})

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isCommand()) return
  const commandInteraction = interaction as CommandInteraction
  const { commandName, member } = commandInteraction

  if (commandName === 'ping') {
    await commandInteraction.reply('Pong!')
  }
  if (commandName === 'fund_eth') {
    const wallet = commandInteraction.options.get('wallet')
    console.log(`Funding wallet ${wallet} of member ${member} with ${env.SEND_ETH_AMOUNT} ETH.`)
    await commandInteraction.reply(`Funding wallet ${wallet} with ${env.SEND_ETH_AMOUNT} ETH.`)
  }
})

void client.login(env.DISCORD_TOKEN)
