# Security Notes

- Default: no auth (dev/demo). Production: enable JWT at `initialize` (extend later).
- Rate limiting: session-level token bucket (defaults: 10 rps / burst 20).
- Data: SSoT stored in Redis when available, else memory-only (ephemeral).
