/**
 * Which project instructions the plugin loads: the `instructionFiles`
 * option.
 *
 * `sirgent-md` loads none of its own, the engine's SIRGENT.md walk standing
 * alone; `sirgent-md-or-agents-md` loads AGENTS.md where the project has no
 * SIRGENT.md; `sirgent-md-and-agents-md` loads AGENTS.md beside SIRGENT.md;
 * `managed-only` loads neither, taking the project's and the person's
 * SIRGENT.md files out of the conversation's context.
 */
export type Mode =
  | 'sirgent-md'
  | 'sirgent-md-or-agents-md'
  | 'sirgent-md-and-agents-md'
  | 'managed-only'
