import type { Plugin } from 'sirgent-ai/testing'

/**
 * A plugin the person installed that drops the memory section.
 */
export const dropping: Plugin = {
  name: 'dropping',
  register(on) {
    on('prompt.section', () => ({ text: null }))
  },
}
