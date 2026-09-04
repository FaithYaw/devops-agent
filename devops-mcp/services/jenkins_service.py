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

    async def trigger_build(self, job_name: str):

        url = (
            f"{self.base_url}"
            f"/job/{job_name}/build"
        )

        async with httpx.AsyncClient() as client:

            response = await client.post(
                url,
                auth=(self.username, self.token)
            )

            response.raise_for_status()

            return {
                "job_name": job_name,
                "triggered": True,
                "status_code": response.status_code
            }