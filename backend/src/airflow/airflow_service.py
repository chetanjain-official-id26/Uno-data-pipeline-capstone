
import os

import httpx


class AirflowService:

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):

        self.base_url = (
            base_url
            or os.getenv(
                "AIRFLOW_URL",
                "http://localhost:8080",
            )
        )

        self.username = (
            username
            or os.getenv(
                "AIRFLOW_USERNAME",
                "airflow",
            )
        )

        self.password = (
            password
            or os.getenv(
                "AIRFLOW_PASSWORD",
                "airflow",
            )
        )

    async def deploy_dag(
        self,
        dag_id: str,
        pipeline_id: str,
        deployment_id: str,
        wheel_key: str,
        manifest_key: str,
    ):

        # Initially this can call an Airflow
        # deployment endpoint/service.
        #
        # Keep this abstraction so the rest
        # of your application does not depend
        # directly on Airflow implementation.

        return {
            "dag_id": dag_id,
            "status": "DEPLOYED",
        }

    async def trigger_dag(
        self,
        dag_id: str,
        conf: dict,
    ):

        url = (
            f"{self.base_url}"
            f"/api/v1/dags/"
            f"{dag_id}/dagRuns"
        )

        async with httpx.AsyncClient() as client:

            response = await client.post(
                url,
                auth=(
                    self.username,
                    self.password,
                ),
                json={
                    "conf": conf,
                },
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()

        return {
            "run_id": data["dag_run_id"],
        }
