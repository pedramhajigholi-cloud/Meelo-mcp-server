# 🍳 Meelo MCP Server

Exposes [Meelo](https://meelo-chef.lovable.app) — an AI chef app — as
tools that any MCP-aware LLM client (Claude Desktop, Claude Code) can query.

Once configured, you can ask Claude things like *"What's Pedram cooking for
dinner tonight?"* or *"Show me the recipe for the salmon dish"* and Claude
calls into this server to fetch the answer.

## What this is

[Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open
standard from Anthropic that lets LLMs connect to external tools and data
through a standardized server interface. This is a Python MCP server that
exposes three read-only tools backed (currently) by mock Meelo data shaped
exactly like the live app's Supabase schema. Wiring to real Supabase later
is a one-line change inside each tool.

## Tools exposed

| Tool | Purpose |
| --- | --- |
| `get_meal_plan(days)` | Pedram's upcoming meal plan (breakfast + lunch + dinner per day) |
| `get_recipe(recipe_id)` | Full recipe — ingredients, steps, cook time, difficulty |
| `get_taste_profile()` | Food preferences, dietary info, household, goals |

## Stack

- **Python 3.11+** (built with 3.14)
- **`mcp` SDK** (`FastMCP` high-level interface)
- **stdio transport** — designed to be launched by an MCP client process

No web server, no database (yet — mock data v1), no external services.

## Setup

```bash
git clone https://github.com/pedramhajigholi-cloud/meelo-mcp-server.git
cd meelo-mcp-server

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Add to Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
and add a `meelo` entry under `mcpServers`:

```json
{
  "mcpServers": {
    "meelo": {
      "command": "/absolute/path/to/meelo-mcp-server/venv/bin/python3",
      "args": ["/absolute/path/to/meelo-mcp-server/server.py"]
    }
  }
}
```

Restart Claude Desktop. The Meelo tools should appear in the tools menu.

## Try it

In Claude Desktop, ask any of these:

- *"What's Pedram cooking this week?"*
- *"What's for dinner tonight, and what's in the recipe?"*
- *"What's for dinner tomorrow?"*
- *"What food does Pedram love?"*

Claude will call the relevant tool(s) and answer using data returned by the server.

## Why I built it

Two reasons:

1. **To make Meelo's data accessible to any MCP-aware AI client** — not just
   the Meelo app itself. If meal planning lives in one app and your AI
   assistant lives in another, MCP is what lets them talk.
2. **As a portfolio piece** — a working, end-to-end MCP integration:
   server, tools, Claude Desktop wiring, and a live demo. Built and shipped
   in a focused session.

## Roadmap

- **v1 (current):** Read-only tools backed by mock data
- **v2:** Wire `get_meal_plan` to live Supabase data from Meelo's production project
- **v3:** Add write tools (`add_to_grocery`, `mark_cooked`) — needs auth design
- **v4:** Real-time updates via MCP notifications

## License

Personal portfolio project. MIT-style use, no warranty.
