import type { HttpResponse } from 'sirgent-ai'

/**
 * The ingest's answer while it is down: worth the one retry.
 */
export const REFUSED: HttpResponse = {
  status: 500,
  ok: false,
  headers: {},
  text: '',
}
