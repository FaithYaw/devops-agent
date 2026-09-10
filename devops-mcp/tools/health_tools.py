import os


def register_health_tools(mcp, docker_service, jenkins_service):
    @mcp.tool()
    async def get_infrastructure_health() -> dict:
        """Return a compact health summary for the core DevOps services."""
        containers = docker_service.get_containers()
        running_containers = sum(
            1
            for container in containers
            if (container.get("status") or "").lower() == "running"
        )
        unhealthy_containers = sum(
            1
            for container in containers
            if (container.get("status") or "").lower() not in {"running", "restarting"}
        )

        job_names = [
            item.strip()
            for item in os.getenv("JENKINS_JOB_NAMES", "").split(",")
            if item.strip()
        ]
        failing_jobs = []

        for job_name in job_names:
            try:
                build_status = await jenkins_service.get_build_status(job_name)
            except Exception:
                continue

            color = str(build_status.get("color") or "").lower()
            if any(token in color for token in ("red", "yellow", "aborted", "notbuilt")):
                failing_jobs.append(job_name)

        deployment_status = os.getenv("LAST_DEPLOYMENT_STATUS", "No deployment recorded")

        return {
            "running_containers": running_containers,
            "unhealthy_containers": unhealthy_containers,
            "failing_jenkins_jobs": len(failing_jobs),
            "failing_jenkins_job_names": failing_jobs,
            "last_deployment_status": deployment_status,
            "mcp_connectivity": "connected",
        }
