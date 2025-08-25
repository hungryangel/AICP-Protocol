
## AICP-Protocol/docs/API_REFERENCE.md
```md
# API Reference (AICP v1.2)

## Methods
- `initialize` → `{ protocolVersion, serverInfo, capabilities }`
- `tools/list` → `{ tools: [...] }`
- `tools/call` (name: route_to_agent | share_context | orchestrate_collaboration)
- `resources/list` → shared-state
- `resources/read` → snapshot text(json)
- `prompts/list`, `prompts/get`

## Schemas (excerpt)
- share_context.inputSchema.context_value: JSON Schema `oneOf` (object/string/number/boolean/array/null)
