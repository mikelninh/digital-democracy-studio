# SafeTrace Open Policy MCP

Read-only MCP server for the Open Policy API and Germany Dashboard.

- Protocol revision targeted: `2025-11-25`
- Transport: `stdio`
- No write, publication, contact, referral or restricted-data tools
- Same versioned JSON documents as the public API

## Run

```bash
python -m pip install -r safetrace/mcp_server/requirements.txt
python -m safetrace.mcp_server.server
```

## Tools

- `list_policy_systems`
- `get_policy_system`
- `list_germany_indicators`
- `get_germany_indicator`
- `search_policy_evidence`
- `compare_policy_systems`

The comparison tool deliberately refuses a single composite policy score.
