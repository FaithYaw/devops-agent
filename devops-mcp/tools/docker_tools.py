from services.docker_service import DockerService


docker_service = DockerService()


def register_docker_tools(mcp):

    @mcp.tool()
    def get_docker_containers() -> list:
        """
         Get all Docker containers and their current status.
        """
        return docker_service.get_containers()

    @mcp.tool()
    def get_container_logs(container_name: str, lines: int = 100) -> str:
        """
        Get the logs of a specific Docker container.

        Args:
            container_name (str): The name or ID of the Docker container.
            lines (int): The number of log lines to retrieve. Default is 100.

        Returns:
            str: The logs of the specified Docker container.
        """
        return docker_service.get_logs(container_name, lines)

    @mcp.tool()
    def restart_container(container_name: str) -> str:
        """
        Restart a specific Docker container.

        Args:
            container_name (str): The name or ID of the Docker container.

        Returns:
            str: A message indicating the result of the restart operation.
        """
        try:
            container = docker_service.client.containers.get(container_name)
            container.restart()
            return f"Container '{container_name}' has been restarted successfully."
        except Exception as e:
            return f"Error restarting container '{container_name}': {str(e)}"