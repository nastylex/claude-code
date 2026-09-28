import type { Mode } from './types'

/**
 * The mode an unset option reads as: AGENTS.md where the project has no
 * SIRGENT.md of its own, the engine's SIRGENT.md walk standing alone where it
 * has one.
 */
export const DEFAULT_MODE: Mode = 'sirgent-md-or-agents-md'
