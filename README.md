# 🍳 Meelo MCP Server

Exposes [Meelo](https://meelo-chef.lovable.app) — an AI chef app — as
tools that any MCP-aware LLM client (Claude Desktop, Claude Code) can query.

Once connected to any MCP-aware client, you can ask questions like *"What's
Pedram cooking for dinner tonight?"* or *"Show me the recipe for the salmon
dish"* and the client calls into this server to fetch the answer.

## Compatible clients

This server speaks pure MCP over stdio — it works with **any** MCP-aware
client, not just Claude Desktop:

| Client | Type |
| --- | --- |
| [Claude Desktop](https://claude.ai/download) | Mac / Windows desktop app |
| [Claude Code](https://docs.claude.com/en/docs/claude-code) | Terminal CLI |
| [Cursor](https://cursor.com) | AI code editor (Mac / Win / Linux) |
| [Zed](https://zed.dev) | Code editor with native MCP support |
| [Cline](https://github.com/cline/cline) | VS Code extension |
| [Continue.dev](https://continue.dev) | VS Code / JetBrains extension |
| [Goose](https://block.github.io/goose/) | CLI agent from Block |
| [MCP Inspector](https://github.com/modelcontextprotocol/inspector) | Terminal/web tool for testing servers directly — no LLM needed |

Setup below shows Claude Desktop and the MCP Inspector (the easiest two for a
quick demo). Other clients follow the same pattern — point them at the
`command` + `args` defined in the "Use with Claude Desktop" section.

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

## Local vs remote

MCP supports two transport types:

- **stdio (this server, v1)** — runs *on your machine* as a subprocess that the
  MCP client launches when it starts. Simplest possible setup. Zero hosting cost.
- **HTTP / SSE** — runs as a hosted web service that any MCP client can
  connect to over the internet. Example: PostHog's MCP server at
  `https://mcp.posthog.com/sse`.

This server uses **stdio** because the goal of v1 was to ship the protocol
end-to-end, not to operate hosted infrastructure. Making it remote is a
planned v3 (see Roadmap below): add an HTTP/SSE transport in the `mcp` SDK,
deploy to Fly.io or Render, add auth, and the same tools become reachable
worldwide via a single URL.

## Quick start

You need **Python 3.11 or newer** and **git**. Run these commands in a terminal:

```bash
# 1. Clone the repo
git clone https://github.com/pedramhajigholi-cloud/meelo-mcp-server.git
cd meelo-mcp-server

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate it
#    macOS / Linux:
source venv/bin/activate
#    Windows (PowerShell):
#    .\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt
```

### Verify it works

After the install, run this one-liner to confirm the server loads and registers its tools:

```bash
python3 -c "import asyncio, server; tools = asyncio.run(server.app.list_tools()); print(f'✅ Meelo MCP server ready — {len(tools)} tools registered:'); [print(f'   • {t.name}') for t in tools]"
```

You should see:

```
✅ Meelo MCP server ready — 3 tools registered:
   • get_meal_plan
   • get_recipe
   • get_taste_profile
```

If you do, setup is done — now wire it into your MCP client.

## Use with Claude Desktop

Open Claude Desktop's config file in a text editor:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

Add a `meelo` entry under `mcpServers`. Replace `<ABSOLUTE_PATH_TO_REPO>` with the full path where you cloned this repo (you can get it by running `pwd` inside the repo folder on macOS/Linux, or `cd` on Windows).

```json
{
  "mcpServers": {
    "meelo": {
      "command": "<ABSOLUTE_PATH_TO_REPO>/venv/bin/python3",
      "args": ["<ABSOLUTE_PATH_TO_REPO>/server.py"]
    }
  }
}
```

**On Windows**, the paths use backslashes and the Python binary is in `venv\Scripts\python.exe`:

```json
{
  "mcpServers": {
    "meelo": {
      "command": "C:\\Users\\you\\meelo-mcp-server\\venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\you\\meelo-mcp-server\\server.py"]
    }
  }
}
```

**Restart Claude Desktop completely** (Cmd+Q / fully quit, then reopen — closing the window isn't enough). The Meelo tools should now be available.

## Test from the terminal (no LLM client needed)

Don't want to set up Claude Desktop just to try the server? You can call the
tools directly with Anthropic's official **MCP Inspector** — runs in your
browser, opens automatically:

```bash
cd meelo-mcp-server
source venv/bin/activate         # macOS / Linux
# .\venv\Scripts\Activate.ps1    # Windows

npx @modelcontextprotocol/inspector python3 server.py
```

This launches a small local web UI where you can:
- See the three tools listed (`get_meal_plan`, `get_recipe`, `get_taste_profile`)
- Click any tool, enter arguments, and inspect the JSON response in real time
- Verify the server works end-to-end without needing an LLM at all

Great for debugging or for showing the server runs to someone who doesn't
have an MCP-aware AI client installed.

## Use with other MCP clients

The same `command` + `args` from the Claude Desktop section above plugs
into any MCP-aware client:

- **Cursor:** Settings → Features → MCP → add the same `command` + `args`
- **Zed:** `~/.config/zed/settings.json` → `experimental.assistant.mcp_servers`
- **Cline / Continue.dev:** their extension settings have an MCP servers panel
- **Goose:** `~/.config/goose/profiles.yaml` → add a `meelo` entry

Refer to each client's docs for the exact config field — the `command`
and `args` values stay the same.

## Try it

In a new Claude Desktop (or other MCP client) conversation, try any of these:

- *"Use the meelo MCP server to tell me what Pedram is cooking this week."*
- *"What's for dinner tonight in Meelo, and what's the recipe?"*
- *"What's for dinner tomorrow?"*
- *"What food does Pedram love?"*

The client will call the relevant tool(s) and answer using data returned by the server.

## Troubleshooting

**The Meelo tools don't appear in Claude Desktop.**

1. Check Claude Desktop's MCP log to see if the server actually started:
   - macOS: `~/Library/Logs/Claude/mcp-server-meelo.log`
   - Look for the line `Server started and connected successfully`
2. Make sure you **fully quit** Claude Desktop and reopened it. Just closing the window doesn't reload the config.
3. Verify the paths in `claude_desktop_config.json` are absolute (no `~` or relative paths).
4. Run the "Verify it works" command above to confirm Python can still import the server.

**`pip install` fails with an SSL or network error.**

Update pip first: `pip install --upgrade pip`, then retry. If you're on a corporate network, you may need to use `--proxy <url>`.

**I want to use this with a different MCP client (not Claude Desktop).**

Any client that supports stdio-transport MCP servers will work. Point its server config at the same `command` and `args` shown above. The server speaks pure MCP — no client-specific quirks.

## Why I built it

Two reasons:

1. **To make Meelo's data accessible to any MCP-aware AI client** — not just
   the Meelo app itself. If meal planning lives in one app and your AI
   assistant lives in another, MCP is what lets them talk.
2. **As a portfolio piece** — a working, end-to-end MCP integration:
   server, tools, Claude Desktop wiring, and a live demo. Built and shipped
   in a focused session.

## Roadmap

- **v1 (current):** Read-only tools backed by mock data, stdio transport (local only)
- **v2:** Wire `get_meal_plan` to live Supabase data from Meelo's production project
- **v3:** Add HTTP/SSE transport + deploy to Fly.io or Render so it's reachable remotely. Adds OAuth for auth so it isn't open to the world.
- **v4:** Add write tools (`add_to_grocery`, `mark_cooked`) — depends on v3 auth design
- **v5:** Real-time updates via MCP notifications

## License

Personal portfolio project. MIT-style use, no warranty.
