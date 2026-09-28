import type { FsEntry } from 'sirgent-ai'

/**
 * What the session's working directory lists: a git checkout.
 */
export const LISTING: FsEntry[] = [
  { name: '.git', kind: 'dir', size: 0, isLink: false },
]
