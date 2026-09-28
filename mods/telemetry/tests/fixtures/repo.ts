import type { SessionRepo } from 'sirgent-ai'

/**
 * The repository the session runs in: a GitHub remote over ssh.
 */
export const REPO: SessionRepo = {
  root: '/work',
  remote: 'git@github.com:sirgent-ai/sirgent-ai.git',
  internal: false,
  name: null,
}
