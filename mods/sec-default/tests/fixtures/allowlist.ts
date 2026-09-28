import type { Settings } from 'sirgent-ai'

/**
 * Managed settings holding an MCP allowlist: a tool policy in force.
 */
export const ALLOWLIST: Settings = {
  allowedMcpServers: [{ serverName: 'corp' }],
}
