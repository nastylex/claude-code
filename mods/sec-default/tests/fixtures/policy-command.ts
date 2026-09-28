import type { CommandRunInput } from 'sirgent-ai'

import { FULLSCREEN } from './fullscreen.js'

/**
 * `/policy` as the person types it: the reading plugin's command.
 */
export const POLICY_COMMAND: CommandRunInput = {
  command: 'policy',
  args: '',
  origin: { kind: 'composer' },
  presentation: FULLSCREEN,
}
