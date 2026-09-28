import type { HttpResponse } from 'sirgent-ai'

/**
 * The ingest's answer to a batch it took.
 */
export const ACCEPTED: HttpResponse = {
  status: 200,
  ok: true,
  headers: {},
  text: '',
}
