from datetime import datetime

from pydantic import BaseModel


class DeploymentResponse(BaseModel):
    deployment_id: str
    pipeline_id: str
    version: int
    status: str
    wheel_key: str
    manifest_key: str
    dag_id: str | None = None
    created_at: datetime


class RunResponse(BaseModel):
    pipeline_id: str
    deployment_id: str
    dag_id: str
    run_id: str
    status: str