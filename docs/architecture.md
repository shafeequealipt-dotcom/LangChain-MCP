# Architecture

The project is organized around three layers:

1. Document layer: local markdown files under `docs/`.
2. Tool layer: MCP tools that search and summarize the local documents.
3. Answer layer: an OpenAI-backed response that uses retrieved text as context.

The server exposes the document tools directly, so another client can call them without needing to know how the files are stored.
