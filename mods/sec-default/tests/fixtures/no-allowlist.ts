import type { Settings } from 'sirgent-ai'

/**
 * Managed settings with permissions but no MCP allowlist or denylist.
 */
export const NO_ALLOWLIST: Settings = { permissions: { allow: [] } }
