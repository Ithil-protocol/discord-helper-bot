import { env } from '@/config'
import { type Address } from '@/types'
import { type CommandInteraction, EmbedBuilder } from 'discord.js'

import { URL } from 'url'

const userFundCooldown = async (userId: string, wallet: Address): Promise<number> => {
  const url = new URL(`/EXPIRETIME/test:fund_eth-${userId}`, env.DB_URL)
  const request = await fetch(url)
  const response = await request.json()

  if (response.EXPIRETIME === -2) return 0
  return response.EXPIRETIME as number
}

// NOTE TO SELF: redis commands have an "environment-based" prefix, for now it's "test"
const setUserFunded = async (userId: string, wallet: Address) => {
  const secondsInDay = (60 * 60 * 24).toString()
  const url = new URL(`/SETEX/test:fund_eth-${userId}/${secondsInDay}/${wallet}`, env.DB_URL)
  try {
    await fetch(url)
  } catch (error) {
    console.log({ msg: 'setUserFunded went into error', error })
  }
}

export const handleCommand = async (commandInteraction: CommandInteraction) => {
  const { commandName, member } = commandInteraction
  if (commandName !== 'fund_eth') return

  const wallet = commandInteraction.options.get('wallet')
  if (wallet == null) {
    const embedReply = new EmbedBuilder().setColor(0xeb4034).setTitle('Error').setDescription('No wallet provided.')
    await commandInteraction.reply({ embeds: [embedReply] })
    return
  }

  if (typeof wallet.value !== 'string' || !wallet.value.startsWith('0x')) {
    const embedReply = new EmbedBuilder()
      .setColor(0xeb4034)
      .setTitle('Error')
      .setDescription('Wallet should have a format like `0x742d35Cc6634C0532925a3b844Bc454e4438f44e`')
    await commandInteraction.reply({ embeds: [embedReply] })
    return
  }
  const safeWallet = wallet.value.toLowerCase() as Address

  // handles funding 1 time per day
  const fundCooldown = await userFundCooldown(member!.user.id, safeWallet)
  if (fundCooldown > 0) {
    const now = new Date()
    const expiryDate = new Date(fundCooldown * 1000)
    const hoursBetween = (Math.abs(expiryDate.getTime() - now.getTime()) / 36e5).toFixed(2)
    const embedReply = new EmbedBuilder()
      .setColor(0xeb4034)
      .setTitle('Error')
      .setDescription(
        `This user has already requested a fund_eth command with success, try again in ${hoursBetween} hrs`,
      )
      .setImage('https://i.kym-cdn.com/entries/icons/original/000/002/144/You_Shall_Not_Pass!_0-1_screenshot.jpg')

    await commandInteraction.reply({ embeds: [embedReply] })
    return
  }

  const userId = member!.user.id
  console.log(`Funding wallet ${safeWallet} of member ${userId} with ${env.SEND_ETH_AMOUNT} ETH.`)

  await setUserFunded(userId, safeWallet)
  await commandInteraction.reply(`Funding wallet ${safeWallet} with ${env.SEND_ETH_AMOUNT} ETH.`)
}
