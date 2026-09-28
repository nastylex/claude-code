import type { InstructionFile } from 'sirgent-ai'

import Frames from '../frames'
import Names from '../names'
import { isProjectOwn } from './is-project-own.js'
import { projectDirOf } from './project-dir-of.js'

/**
 * Whether a handed instruction file is a SIRGENT.md, `.sirgent/SIRGENT.md` or
 * SIRGENT.local.md of a directory on the walk down to the session's root.
 *
 * What makes a project "have a SIRGENT.md of its own" for
 * `sirgent-md-or-agents-md`, the same files the Read walk asks for; a rules
 * file, an imported file or an added directory's SIRGENT.md is not one.
 *
 * @param file the handed instruction file
 * @param root the session's project root, absolute
 * @returns true for the project's own SIRGENT.md files on the walk
 */
export function isSirGentFileOnWalk(
  file: InstructionFile,
  root: string,
): boolean {
  const isOwnSirGentFile =
    isProjectOwn(file) &&
    file.parent === undefined &&
    Names.SIRGENT_NAMES.some(name =>
      Frames.normalSpellingOf(file.path).endsWith(`/${name}`),
    )

  if (!isOwnSirGentFile) {
    return false
  }

  const dir = projectDirOf(file.path)
  const spelledRoot = Frames.normalSpellingOf(root)

  return dir === spelledRoot || Frames.isBelow(spelledRoot, dir)
}
