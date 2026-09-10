import httpx


class JenkinsService:

    def __init__(
        self,
        base_url: str,
        username: str,
        token: str
    ):
        self.base_url = base_url
        self.username = username
        self.token = token

    async def get_job(self, job_name: str):

        url = (
            f"{self.base_url}"
            f"/job/{job_name}/api/json"
        )

        async with httpx.AsyncClient() as client:

            response = await client.get(
                url,
                auth=(self.username, self.token)
            )

            response.raise_for_status()

            return response.json()

    async def get_build_status(self, job_name: str):

        job = await self.get_job(job_name)

        return {
            "job_name": job_name,
            "buildable": job.get("buildable"),
            "in_queue": job.get("inQueue"),
            "color": job.get("color"),
            "last_build": (job.get("lastBuild") or {}).get("number"),
            "last_completed_build": (job.get("lastCompletedBuild") or {}).get("number"),
            "last_successful_build": (job.get("lastSuccessfulBuild") or {}).get("number"),
            "last_failed_build": (job.get("lastFailedBuild") or {}).get("number"),
            "url": job.get("url")
        }

    async def get_job_parameters(self, job_name: str):

        url = (
            f"{self.base_url}"
            f"/job/{job_name}/api/json?tree=actions[parameterDefinitions[*]]"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                auth=(self.username, self.token),
            )
            response.raise_for_status()

            job = response.json()
            actions = job.get("actions", [])
            parameter_definitions = []

            for action in actions:
                params = action.get("parameterDefinitions") or []
                for param in params:
                    parameter_definitions.append({
                        "name": param.get("name"),
                        "type": param.get("type"),
                        "description": param.get("description"),
                        "default_parameter_value": (param.get("defaultParameterValue") or {}).get("value"),
                        "choices": param.get("choices") or [],
                    })

            return {
                "job_name": job_name,
                "parameters": parameter_definitions,
            }

    async def trigger_build(self, job_name: str, parameters: dict | None = None, cause: str | None = None):

        payload = {}
        if cause:
            payload["cause"] = cause

        if parameters:
            payload.update(parameters)
            url = (
                f"{self.base_url}"
                f"/job/{job_name}/buildWithParameters"
            )
        else:
            url = (
                f"{self.base_url}"
                f"/job/{job_name}/build"
            )

        async with httpx.AsyncClient() as client:

            response = await client.post(
                url,
                auth=(self.username, self.token),
                data=payload or None,
            )

            response.raise_for_status()

            return {
                "job_name": job_name,
                "triggered": True,
                "status_code": response.status_code,
                "parameters": parameters or {},
                "cause": cause,
            }