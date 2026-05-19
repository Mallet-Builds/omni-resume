# Omni Resume Antigravity Plugin

This plugin exposes the omni-resume index inside Antigravity through MCP.

## Install

Copy this folder into one of Antigravity's plugin locations:

- `~/.gemini/config/plugins/omni-resume`
- `<workspace>/.agents/plugins/omni-resume`

Then make sure `omni-resume-mcp` is installed and on your `PATH`.

## What it is for

- Searching prior coding-agent sessions
- Getting exact resume commands
- Refreshing the local index after backfills or new ingestion

## What it is not for

- It is not the ingestion pipeline.
- It does not replace Honcho or the source-specific daemons.
- It does not mirror every chat transcript into memory.

