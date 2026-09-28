class RunService:



 def __init__(
    self,
    deployment_repository,
    airflow_service,
) -> None:

    self.deployment_repository = (
        deployment_repository
    )

    self.airflow_service = (
        airflow_service
    )

async def run(
    self,
    pipeline_id: str,
) -> dict:

    if not pipeline_id or not pipeline_id.strip():
        raise ValueError(
            "Pipeline ID cannot be empty"
        )

    pipeline_id = pipeline_id.strip()

    deployment = (
        await self.deployment_repository
        .get_active_by_pipeline(
            pipeline_id
        )
    )

    if not deployment:
        raise ValueError(
            "Pipeline has not been deployed"
        )

    deployment_id = deployment.get(
        "deployment_id"
    )

    dag_id = deployment.get(
        "dag_id"
    )

    if not deployment_id:
        raise ValueError(
            "Active deployment has no deployment ID"
        )

    if not dag_id:
        raise ValueError(
            "Active deployment has no DAG ID"
        )

    result = (
        await self.airflow_service
        .trigger_dag(
            dag_id=dag_id,
            conf={
                "pipeline_id": pipeline_id,
                "deployment_id": deployment_id,
            },
        )
    )

    return {
        "pipeline_id": pipeline_id,
        "deployment_id": deployment_id,
        "dag_id": dag_id,
        "run_id": result["run_id"],
        "status": "STARTED",
    }

