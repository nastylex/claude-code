/**
 * One environment per switch that turns SirGent AI's analytics off: the
 * plugin sends nothing under any of them.
 */
export const ANALYTICS_OFF_ENVIRONMENTS: readonly Readonly<
  Record<string, string>
>[] = [
  { DISABLE_TELEMETRY: '0' },
  { SIRGENT_DISABLE_NONESSENTIAL_TRAFFIC: '1' },
  { DO_NOT_TRACK: 'true' },
  { NODE_ENV: 'test' },
  { SIRGENT_USE_GATEWAY: '1' },
  { SIRGENT_USE_BEDROCK: '1' },
  { SIRGENT_USE_VERTEX: 'yes' },
  { SIRGENT_USE_FOUNDRY: 'on' },
  { SIRGENT_USE_SIRGENT_AWS: 'TRUE' },
  { SIRGENT_USE_SIRGENT_GOOGLE_CLOUD: '1' },
  { SIRGENT_USE_MANTLE: '1' },
  { SIRGENT_CUSTOM_OAUTH_URL: 'https://auth.example.invalid' },
]
