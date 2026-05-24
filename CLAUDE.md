# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
rake serve       # local dev server with live reload
rake build       # one-off build to _site/
rake pdf         # export resume.pdf via headless Chrome (requires _data/pii.yml)
rake pii:init    # copy _data/pii.example.yml → _data/pii.yml for first-time setup
```

## Architecture

Jekyll site deployed to GitHub Pages (`nicky-isaacs.github.io`).

**Two-tier PII system** — the key architectural invariant:

- `_data/pii.yml` is **gitignored**. It holds real contact info (name, email, phone, address, LinkedIn) and is only present in local builds. Never commit this file.
- `_config.yml` holds public author info (`author.name`, `author.github`) that is intentionally published.
- `_layouts/resume.html` branches on `{% if site.data.pii %}`: with the file present it renders full contact details; without it the header shows "Contact information available upon request". This lets the same template serve both the public site and a private PDF export.

**Content data** — `_data/resume.yml` holds all experience, education, and skills as structured YAML. The resume layout iterates over it; there is no prose resume content in Markdown.

**PII guard** — `.claude/hooks/pii-guard.py` is a Claude Code Stop hook (registered in `.claude/settings.json`) that scans git-modified files for the owner's last name, email, phone, street address, and LinkedIn URL before each session ends. It exits 2 (block + re-invoke Claude) if a hit is found. The allowlist in the hook permits `_config.yml`, `about.md`, and template/asset directories where the name appears intentionally.
