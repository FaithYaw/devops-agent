import docker


class DockerService:

    #Runs when a DockerService object is created.
    def __init__(self):
        #Connects to Docker using environment settings (like Docker socket / local Docker config).
        self.client = docker.from_env()

    def get_containers(self):
        #This lists all containers, including stopped ones, not just running ones.
        containers = self.client.containers.list(all=True)

        #This returns a list of dictionaries, each containing the ID, name, status, and image of a container.
        return [
            {
                "id": container.short_id,
                "name": container.name,
                "status": container.status,
                "image": container.attrs.get("Config", {}).get("Image", ""),
            }
            for container in containers
        ]

    def get_logs(self,container_name:str,lines:int=100):
        #This retrieves the logs of a specific container, limited to a certain number of lines.
        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=lines).decode("utf-8")
            return logs
        except Exception as e:
            return str(e)