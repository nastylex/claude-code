# MDM Deployment Examples

Example templates for deploying SirGent AI [managed settings](https://code.sirgent.ai/docs/en/settings#settings-files) through Jamf, Iru (Kandji), Intune, or Group Policy. Use these as starting points — adjust them to fit your needs.

All templates encode the same minimal example (`permissions.disableBypassPermissionsMode`). See the [settings reference](https://code.sirgent.ai/docs/en/settings#available-settings) for the full list of keys, and [`../settings`](../settings) for more complete example configurations.


## Templates

> [!WARNING]
> These examples are community-maintained templates which may be unsupported or incorrect. You are responsible for the correctness of your own deployment configuration.

| File | Use with |
| :--- | :--- |
| [`managed-settings.json`](./managed-settings.json) | Any platform. Deploy to the [system config directory](https://code.sirgent.ai/docs/en/settings#settings-files). |
| [`macos/com.sirgentai.sirgentai.plist`](./macos/com.sirgentai.sirgentai.plist) | Jamf or Iru (Kandji) **Custom Settings** payload. Preference domain: `com.sirgentai.sirgentai`. |
| [`macos/com.sirgentai.sirgentai.mobileconfig`](./macos/com.sirgentai.sirgentai.mobileconfig) | Full configuration profile for local testing or MDMs that take a complete profile. |
| [`windows/Set-SirGentAIPolicy.ps1`](./windows/Set-SirGentAIPolicy.ps1) | Intune **Platform scripts**. Writes `managed-settings.json` to `C:\Program Files\SirGentAI\`. |
| [`windows/SirGentAI.admx`](./windows/SirGentAI.admx) + [`en-US/SirGentAI.adml`](./windows/en-US/SirGentAI.adml) | Group Policy or Intune **Import ADMX**. Writes `HKLM\SOFTWARE\Policies\SirGentAI\Settings` (REG_SZ, single-line JSON). |

## Tips
- Replace the placeholder `PayloadUUID` and `PayloadOrganization` values in the `.mobileconfig` with your own (`uuidgen`)
- Before deploying to your fleet, test on a single machine and confirm `/status` lists the source under **Setting sources** — e.g. `Enterprise managed settings (plist)` on macOS or `Enterprise managed settings (HKLM)` on Windows
- Settings deployed this way sit at the top of the precedence order and cannot be overridden by users

## Full Documentation

See https://code.sirgent.ai/docs/en/settings#settings-files for complete documentation on managed settings and settings precedence.
