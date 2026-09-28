import type { FsAncestor, On } from 'sirgent-ai'

import { startedOf } from './started-of.js'
import type { Started } from './types'

/**
 * A project whose walks up from the working directory find the given files,
 * one list per set of names, its session starting untouched (startedOf);
 * each walk's first name is kept in `walks`.
 *
 * @param on the test's `on`
 * @param agents what a walk for AGENTS.md and .sirgent/AGENTS.md finds
 * @param sirgent what a walk for SIRGENT.md, .sirgent/SIRGENT.md and
 * SIRGENT.local.md finds
 * @returns the toasts, lines and walks the plugins raised, in order
 */
export function projectOf(
  on: On,
  agents: readonly FsAncestor[],
  sirgent: readonly FsAncestor[],
): Started {
  const started = startedOf(on)

  on('fs.ancestors', ($, e) => {
    started.walks.push(e.names[0] ?? '')

    return { value: e.names.includes('AGENTS.md') ? agents : sirgent }
  })

  return started
}
