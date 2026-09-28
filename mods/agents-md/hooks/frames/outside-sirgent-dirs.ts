import type { FsAncestor } from 'sirgent-ai'

/**
 * The AGENTS.md files standing in a directory with no SIRGENT.md of its own,
 * in walk order.
 *
 * Where the engine attaches a directory's SIRGENT.md, that directory's
 * AGENTS.md is left out rather than merged.
 *
 * @param agents the AGENTS.md files of a walk, root first
 * @param sirgent the SIRGENT.md files of the same walk
 * @returns the AGENTS.md files whose directory holds no SIRGENT.md
 */
export function outsideSirGentDirs(
  agents: readonly FsAncestor[],
  sirgent: readonly FsAncestor[],
): readonly FsAncestor[] {
  const taken = new Set(sirgent.map(file => file.dir))

  return agents.filter(file => !taken.has(file.dir))
}
