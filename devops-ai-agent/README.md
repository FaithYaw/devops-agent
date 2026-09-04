# DevOps AI Agent

This project contains a DevOps assistant that can call MCP tools to inspect infrastructure.

## Run the UI locally

1. Start the MCP server from the `devops-mcp` project.
2. Open a terminal in `devops-ai-agent`.
3. Install dependencies:
   `uv sync`
4. Start the chat UI:
   `uv run streamlit run app.py`

Both the agent and MCP server load shared env config from the repository root:
- `.env` selects the environment with `APP_ENV=local` or `APP_ENV=production`
- `.env.local` contains local values
- `.env.production` contains production values

The UI will use `MCP_SERVER_URL` from the selected env file.

## Run in terminal mode

`uv run python agent.py`

## Run with Docker Compose

From the repository root:

```bash
docker compose up --build
```

Services:
- Streamlit AI agent UI: `http://localhost:8501`
- MCP server endpoint: `http://localhost:9090/mcp`

For deployment, set secrets in:
- `.env.production` for `OPENAI_API_KEY`
- `.env.production` for Jenkins-related variables

The MCP container mounts `/var/run/docker.sock` so its Docker tools can inspect and restart containers on the EC2 host.
