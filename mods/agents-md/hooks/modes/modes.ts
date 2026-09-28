import type { Mode } from './types'

/**
 * Every mode, in the order the option's description names them.
 */
export const MODES: readonly Mode[] = [
  'sirgent-md',
  'sirgent-md-or-agents-md',
  'sirgent-md-and-agents-md',
  'managed-only',
]
