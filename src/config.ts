import { createEnv } from '@t3-oss/env-core'
import { z } from 'zod'

// eslint-disable-next-line @typescript-eslint/no-var-requires
if (process.env.NODE_ENV !== 'production') require('dotenv').config({ path: '.env.development' })

export const env = createEnv({
  clientPrefix: 'PUBLIC_',
  server: {
    PRIVATE_KEY: z.string().min(1),
    RPC_URL: z.string().url(),

    DB_URL: z.string().url(),
    DISCORD_TOKEN: z.string().min(1),
    DISCORD_APP_ID: z.string().min(1),

    SEND_ETH_AMOUNT: z.string().min(1),
    TOKENS: z.string().min(1),
  },
  client: {},
  runtimeEnv: process.env, // or `import.meta.env`, or similar
})
