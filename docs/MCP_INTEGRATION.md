# MCP Integration Guide (AICP v1.2)

- WS Endpoint: `ws://<host>:8765/mcp`
- Initialize:
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"your-client","version":"x.y"}}}
Tools:

route_to_agent(message, target_capabilities?, context?)

share_context(context_key, context_value)

orchestrate_collaboration(task, agents?)

Resources:

aicp://shared-state (read-only snapshot)