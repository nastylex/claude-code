import { SENDING_ENV } from './sending-env.js'

/**
 * SENDING_ENV inside a GitHub Actions workflow running the SirGent AI
 * action from a pull request.
 */
export const GITHUB_ACTION_ENV: Readonly<Record<string, string>> = {
  ...SENDING_ENV,
  CI: 'true',
  GITHUB_ACTIONS: 'true',
  GITHUB_EVENT_NAME: 'pull_request',
  RUNNER_OS: 'Linux',
  RUNNER_ENVIRONMENT: 'github-hosted',
  GITHUB_ACTION_PATH: '/runner/_actions/sirgent-ai/sirgent-action/v1',
  GITHUB_ACTOR_ID: '11',
  GITHUB_REPOSITORY_ID: '22',
  GITHUB_REPOSITORY_OWNER_ID: '33',
  SIRGENT_ENTRYPOINT: 'sirgent-ai-github-action',
  SIRGENT_ACTION: '1',
}
