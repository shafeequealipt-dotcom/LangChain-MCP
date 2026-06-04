# Contributing

## Goals

Keep changes small, documented, and safe to publish.

## Local Workflow

1. Make the change in a feature branch.
2. Run the unit tests.
3. Run a live CLI smoke test when the change touches OpenAI or MCP transport behavior.
4. Scan for secrets before committing.
5. Ensure only intended files are staged.

## Code Standards

- Prefer explicit, readable Python over clever one-liners.
- Keep network calls behind small helper functions.
- Keep the README synchronized with the actual behavior.
- Update `docs/` when the architecture, configuration, or security story changes.

## Secret Policy

- Never commit `.env`, tokens, logs, or caches.
- If a secret is exposed, rotate it before merging or publishing.

## GitHub Publishing

- Commit messages should be short and descriptive.
- Do not push unfinished work unless it is explicitly marked as such.
