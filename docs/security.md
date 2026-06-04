# Security

Keep the following local only:

- `.env`
- API keys
- logs
- generated caches

If a key ever appears in a committed file or pushed log, rotate it immediately and remove the secret from history before treating the issue as resolved.
