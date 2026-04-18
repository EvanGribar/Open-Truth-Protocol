from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env.local", env_file_encoding="utf-8"
    )

    kafka_bootstrap_servers: str = Field(alias="KAFKA_BOOTSTRAP_SERVERS")
    kafka_security_protocol: str = Field(default="PLAINTEXT", alias="KAFKA_SECURITY_PROTOCOL")

    s3_endpoint: str = Field(alias="S3_ENDPOINT")
    s3_bucket_intake: str = Field(alias="S3_BUCKET_INTAKE")
    s3_bucket_models: str = Field(alias="S3_BUCKET_MODELS")
    aws_access_key_id: str = Field(alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(alias="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")

    temporal_host: str = Field(alias="TEMPORAL_HOST")
    temporal_namespace: str = Field(default="default", alias="TEMPORAL_NAMESPACE")
    temporal_task_queue: str = Field(default="otp-orchestrator", alias="TEMPORAL_TASK_QUEUE")

    redis_url: str = Field(alias="REDIS_URL")

    otp_env: str = Field(default="development", alias="OTP_ENV")
    otp_log_level: str = Field(default="INFO", alias="OTP_LOG_LEVEL")
    otp_api_host: str = Field(default="127.0.0.1", alias="OTP_API_HOST")
    otp_api_port: int = Field(default=8000, alias="OTP_API_PORT")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
