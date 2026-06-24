# Rapha

<p align="center">
  <strong>Rapha</strong>
</p>

<p align="center">
  A private, self-hosted AI workspace for healthcare professionals.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="docs/setup.md">Setup Guide</a> ·
  <a href="CONTRIBUTING.md">Contributing</a> ·
  <a href="ROADMAP.md">Roadmap</a>
</p>

<p align="center">
  <strong>Rapha 1.0.0-rapha.1</strong> · OpenDoctor bridge · Clinical templates · Privacy gate
</p>

---

## Quick Start

> `dev` is Rapha's integration branch. Upstream updates are reviewed monthly and validated before promotion.

```bash
git clone https://github.com/carlosglz1912/rapha.git
cd rapha
cp .env.example .env
docker compose up -d --build
```

Open `http://localhost:7100` when the containers are healthy. The first admin password is printed in `docker compose logs rapha`.

Native installs, GPU notes, Windows/macOS instructions, HTTPS, and configuration live in the [setup guide](docs/setup.md).

## Features

- **Chat + Agents** — local/API models, tools, MCP, files, shell, skills, and memory.
- **Cookbook** — hardware-aware model recommendations, downloads, and serving.
- **Deep Research** — multi-step web research with source reading and report generation.
- **Compare** — blind side-by-side model testing and synthesis.
- **Documents** — writing-first editor with AI edits, suggestions, Markdown, HTML, CSV, and syntax highlighting.
- **Email** — IMAP/SMTP inbox with triage, tags, summaries, reminders, and reply drafts.
- **Notes, Tasks + Calendar** — reminders, todos, scheduled agent tasks, and CalDAV sync.
- **Extras** — gallery/image editor, themes, uploads, web search, presets, sessions, and 2FA.

## Demo

A full hover-to-play tour lives on the landing page: [`docs/index.html`](docs/index.html).

## Contributing

Help is welcome. The best entry points are fresh-install testing, provider setup bugs, mobile/editor polish, docs, and small focused refactors. See [CONTRIBUTING.md](CONTRIBUTING.md) and [ROADMAP.md](ROADMAP.md).

## Security

Rapha is a self-hosted workspace with powerful local tools. Keep auth enabled, keep private data out of Git, and do not expose raw model/service ports publicly. Deployment details are in the [setup guide](docs/setup.md#security-notes).

## Upstream

Rapha tracks the upstream repository as a reviewed base. Product-specific code stays in thin compatibility,
clinical, and OpenDoctor bridge layers; see [docs/VISION.md](docs/VISION.md).

## License

AGPL-3.0-or-later -- see [LICENSE](LICENSE) and [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md).
