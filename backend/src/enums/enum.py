from enum import Enum


class PipelineStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    FAILED = "failed"
    COMPLETED = "completed"


class ConnectionType(str, Enum):
    POSTGRESQL = "postgresql"
    COCKROACHDB = "cockroachdb"
    MYSQL = "mysql"


class WriteMode(str, Enum):
    APPEND = "append"
    OVERWRITE = "overwrite"


class PipelineRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class TargetType(str, Enum):
    TABLE = "table"
    FILE = "file"