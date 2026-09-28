import type { SessionEndInput } from 'sirgent-ai'

/**
 * The session as it ends: the person left.
 */
export const ENDED: SessionEndInput = {
  reason: 'prompt_input_exit',
  sessionId: 'the-session',
  resume: { id: 'the-session' },
}
