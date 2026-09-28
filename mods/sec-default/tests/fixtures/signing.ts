import type { Plugin } from 'sirgent-ai/testing'

/**
 * The organization's own plugin, in its last tier, which signs the section.
 */
export const signing: Plugin = {
  name: 'signing',
  tier: 'append',
  register(on) {
    on('prompt.section', ($, e, next) =>
      next({ ...e, text: `${e.text} (signed)` }),
    )
  },
}
