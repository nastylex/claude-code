import type { SessionStartInput } from 'sirgent-ai'

/**
 * An interactive terminal session two directories under /repo.
 */
export const SESSION: SessionStartInput = {
  surface: 'terminal',
  isInteractive: true,
  cwd: '/repo/a/b',
}
