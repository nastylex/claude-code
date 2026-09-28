import type { SessionStartInput } from 'sirgent-ai'

/**
 * An interactive terminal session in the linked worktree /main/wt.
 */
export const WORKTREE_SESSION: SessionStartInput = {
  surface: 'terminal',
  isInteractive: true,
  cwd: '/main/wt',
}
