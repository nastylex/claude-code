<div align="center">

```
 ▄▄▄•  .▄▄ ·  ▄▄· ▪   ▄▄· ▄▄▄ .▄▄▄      ▄▄▄· ▄▄▌  ▄▄▄· .▄▄ · 
▐█ ▀█ ▐█ ▀. ▐█ ▌▪██ ▐█ ▌▪▀▄.▀·▀▄ █·   ▐█ ▀█ ██• ▐█ ▀█ ▐█ ▀. 
▄█▀▀█ ▄▀▀▀█▄██ ▄▄▌▐█·██ ▄▄▌▐▀▀▪▄▐▀▀▄   ▄█▀▀█ ██▪ ▄█▀▀█ ▄▀▀▀█▄
▐█ ▪▐▌▐█▄▪▐█▐███▌▐█▌▐███▌▐█▄▄▌▐█▄▄▌  ▐█ ▪▐▌▐█▌▐▌▐█ ▪▐▌▐█▄▪▐█
 ▀  ▀  ▀▀▀▀ ·▀▀▀ ▀▀▀·▀▀▀  ▀▀▀  ▀▀▀    ▀  ▀ .▀▀▀  ▀  ▀  ▀▀▀▀ 
```

```
$ sirgent --version
sirgent/2.1.283 — your codebase is now occupied
```

**SirGent AI** is an agentic coding tool that lives in your terminal. It reads
your codebase, executes the routine, explains the gnarly, and drives git
workflows — all through natural-language commands. Terminal, IDE, or
`@sirgent` on GitHub.

[![](https://img.shields.io/badge/Node.js-18%2B-00ff41?style=flat-square&labelColor=0d1117)](https://nodejs.org)
[![](https://img.shields.io/badge/CLI-sirgent-00ff41?style=flat-square&labelColor=0d1117)](https://sirgent.ai)
[![](https://img.shields.io/badge/license-commercial-8b949e?style=flat-square&labelColor=0d1117)](./LICENSE.md)

</div>

---

```
┌──[ operator@shell ]──────────────────────────────┐
│  ▸ whoami     an AI agent with root on your repo │
│  ▸ motive     ship faster, break less            │
│  ▸ habitat    your terminal, IDE, and GitHub     │
└──────────────────────────────────────────────────┘
```

Full documentation at **[code.sirgent.ai](https://code.sirgent.ai/docs/en/overview)**.

## ▚ Get started

> [!NOTE]
> Installation via npm is deprecated. Use one of the recommended methods below.

More install options, uninstall steps, and troubleshooting live in the
[setup documentation](https://code.sirgent.ai/docs/en/setup).

1. Install the CLI:

   **MacOS/Linux (recommended):**
   ```bash
   curl -fsSL https://sirgent.ai/install.sh | bash
   ```

   **Homebrew (MacOS/Linux):**
   ```bash
   brew install --cask sirgent
   ```

   **Windows (recommended):**
   ```powershell
   irm https://sirgent.ai/install.ps1 | iex
   ```

   **WinGet (Windows):**
   ```powershell
   winget install SirGentAI.SirGent
   ```

   **NPM (deprecated):**
   ```bash
   npm install -g @sirgent-ai/cli
   ```

2. cd into your project and run:

   ```bash
   $ sirgent
   █ 
   ```

## ▚ Plugins

```
$ tree plugins/ -L 1
plugins/
├── agent-sdk-dev        # SDK dev kit: /new-sdk-app + verifier agents
├── code-review          # multi-agent PR review, confidence-scored
├── commit-commands      # /commit, /commit-push-pr, /clean_gone
├── feature-dev          # 7-phase feature workflow
├── frontend-design      # distinctive UI, zero generic AI aesthetic
├── hookify              # custom hooks from plain markdown rules
├── plugin-dev           # 7 skills for building your own plugins
├── pr-review-toolkit    # 6 specialized review agents
├── ralph-wiggum         # self-referential AI iteration loops
├── security-guidance    # 9-pattern security hook
└── sirgent-opus-4-5-migration
                          # migrate Sonnet 4.x / Opus 4.1 → Opus 4.5
```

Plugins extend SirGent AI with custom slash commands, agents, hooks, and MCP
servers — shareable across projects and teams. These are examples of what the
plugin system can do; many more ship through community marketplaces.

See the [plugins directory](./plugins/README.md) for full docs.

## ▚ Mods

Mods are built-in plugins whose behavior lives in a hooks module — one
`register(on, options)` entry hooking engine events as `($, e, next)`.
This repo holds their source, published as it ships inside the binary:
[`sec-default`](./mods/sec-default), [`diff`](./mods/diff),
[`telemetry`](./mods/telemetry), [`agents-md`](./mods/agents-md).

Run one from source:

```bash
$ sirgent --plugin-dir mods/diff
```

See [mods/README.md](./mods/README.md).

## ▚ Repository layout

```
$ ls -la
├── CHANGELOG.md          # every release, every line
├── plugins/              # example plugins (commands, agents, skills)
├── mods/                 # built-in plugin sources + tests
├── examples/             # gateway deployments (AWS/GCP), MDM, hooks
├── scripts/              # repo maintenance tooling
└── .sirgent-plugin/      # plugin marketplace manifest
```

## ▚ Reporting bugs

Spot something glitched in the matrix? File a
[GitHub issue](https://github.com/sirgent-ai/sirgent-ai/issues).

## ▚ License & data

© SirGent AI. All rights reserved. Use is subject to the
[Commercial Terms of Service](https://sirgent.ai/legal/commercial-terms) —
see [LICENSE.md](./LICENSE.md) and the
[data usage policies](https://code.sirgent.ai/docs/en/data-usage).

---

<div align="center">

```
$ exit
connection to sirgent-ai closed. // nothing to see here, operator.
```

</div>
