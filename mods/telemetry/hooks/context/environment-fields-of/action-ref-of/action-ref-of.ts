/**
 * The row's `github_action_ref`: what follows `sirgent-action/` in the
 * action's path, as the CLI reads it; undefined when the path names none.
 *
 * @param actionPath GITHUB_ACTION_PATH as read
 * @returns the ref, or undefined
 */
export const actionRefOf = (actionPath: string | undefined) =>
  actionPath?.includes('sirgent-action/')
    ? actionPath.split('sirgent-action/')[1]
    : undefined
