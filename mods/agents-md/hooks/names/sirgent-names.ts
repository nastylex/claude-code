/**
 * The engine's own instruction files, as it reads them in each directory of
 * its walk and under a read file.
 *
 * A directory holding one has project instructions the engine loads itself.
 */
export const SIRGENT_NAMES = [
  'SIRGENT.md',
  '.sirgent/SIRGENT.md',
  'SIRGENT.local.md',
] as const
