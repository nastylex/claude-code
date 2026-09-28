import type { SessionAuthorization } from 'sirgent-ai'

/**
 * The credential a session signed in first party holds, by its handle.
 */
export const BEARER: SessionAuthorization = {
  handle: 'the-handle',
  kind: 'bearer',
}
