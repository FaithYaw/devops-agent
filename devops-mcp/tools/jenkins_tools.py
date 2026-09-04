from services.jenkins_service import JenkinsService


def register_jenkins_tools(mcp, jenkins_service):

    @mcp.tool()
    async def get_jenkins_job(
        job_name: str
    ) -> dict:
        """
        Get the current status of a Jenkins job.
        """

        return await jenkins_service.get_job(
            job_name
        )

    @mcp.tool()
    async def get_jenkins_build_status(
        job_name: str
    ) -> dict:
        """
        Get build status information for a Jenkins job.
        """

        return await jenkins_service.get_build_status(
            job_name
        )

    @mcp.tool()
    async def trigger_jenkins_build(
        job_name: str
    ) -> dict:
        """
        Trigger a Jenkins build by job name.
        """

        return await jenkins_service.trigger_build(
            job_name
        )