import type { Args } from 'sirgent-ai'
import type { MockClock } from 'sirgent-ai/testing'

/**
 * What a test reads back of its session: each post to the ingest, each file
 * read and program run the plugin made, each debug line, and the clock.
 */
export type SentSession = {
  readonly posts: Args<'http.fetch'>[]
  readonly reads: string[]
  readonly runs: Args<'process.run'>[]
  readonly lines: string[]
  readonly clock: MockClock
}
