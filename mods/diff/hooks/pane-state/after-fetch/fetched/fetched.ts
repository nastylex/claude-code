import type { SessionMessage } from 'sirgent-ai'

import type Git from '../../../git'

/**
 * What one refresh read: how the diff fetch ended and the transcript rows.
 */
export type Fetched = {
  outcome: Git.FetchOutcome
  messages: readonly SessionMessage[]
}
