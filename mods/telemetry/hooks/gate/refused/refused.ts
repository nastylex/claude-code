/**
 * The answer a caller outside the served tiers gets from `$.telemetry`: its
 * promise rejects with this, and the host notes it in the debug log.
 */
export const REFUSED = {
  deny: '$.telemetry serves the plugins built into SirGent AI alone',
} as const
