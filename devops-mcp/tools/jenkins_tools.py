from typing import Annotated

from pydantic import Field

from services.jenkins_service import JenkinsService


def register_jenkins_tools(mcp, jenkins_service):

    @mcp.tool()
    async def get_jenkins_job(
        job_name: Annotated[
            str,
            Field(description="Jenkins job name, including any folder path if the job is nested, e.g. 'platform/backend-deploy'."),
        ]
    ) -> dict:
        """
        Get the current Jenkins job metadata and configuration.
        """

        return await jenkins_service.get_job(job_name)

    @mcp.tool()
    async def get_jenkins_build_status(
        job_name: Annotated[
            str,
            Field(description="Jenkins job name whose latest build status should be returned."),
        ]
    ) -> dict:
        """
        Get build status information for a Jenkins job.
        """

        return await jenkins_service.get_build_status(job_name)

    @mcp.tool()
    async def get_jenkins_job_parameters(
        job_name: Annotated[
            str,
            Field(description="Jenkins job name to inspect for parameterized build inputs."),
        ]
    ) -> dict:
        """
        List the parameter definitions for a Jenkins job so the agent can populate trigger values correctly.
        """

        return await jenkins_service.get_job_parameters(job_name)

    @mcp.tool()
    async def trigger_jenkins_build(
        job_name: Annotated[
            str,
            Field(description="Jenkins job name to trigger. Use the full path for jobs inside folders."),
        ],
        parameters: Annotated[
            dict[str, str] | None,
            Field(
                default=None,
                description="Optional build parameters for parameterized Jenkins jobs. Example: {'branch': 'main', 'environment': 'prod'}.",
            ),
        ] = None,
        cause: Annotated[
            str | None,
            Field(default=None, description="Optional reason or owner note attached to the Jenkins build trigger."),
        ] = None,
    ) -> dict:
        """
        Trigger a Jenkins build by job name.

        Use `parameters` for parameterized jobs such as deploy or release pipelines.
        """

        return await jenkins_service.trigger_build(
            job_name,
            parameters=parameters,
            cause=cause,
        )