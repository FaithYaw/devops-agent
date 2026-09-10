import os
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

from services.docker_service import DockerService
from services.jenkins_service import JenkinsService
from tools.docker_tools import register_docker_tools
from tools.health_tools import register_health_tools
from tools.jenkins_tools import register_jenkins_tools

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / f".env.{os.getenv('APP_ENV', 'local')}"
load_dotenv(ENV_FILE)

JENKINS_URL = os.getenv("JENKINS_URL")
JENKINS_USERNAME = os.getenv("JENKINS_USERNAME")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN")
mcp = MCPServer("DevOps MCP")

docker_service = DockerService()
register_docker_tools(mcp)
jenkins_service = JenkinsService(JENKINS_URL, JENKINS_USERNAME, JENKINS_TOKEN)
register_jenkins_tools(mcp, jenkins_service)
register_health_tools(mcp, docker_service, jenkins_service)


@mcp.tool()
def ping() -> str:
    """Check whether the DevOps MCP server is working."""
    return "DevOps MCP is alive"


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", "9090")),
    )