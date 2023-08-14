from dotenv import find_dotenv
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    # general
    py_version: str
    replicas: int
    max_surge: int
    docker_account: str

    # auth
    mysql_host: str
    mysql_user: str
    mysql_password: str
    mysql_db: str
    mysql_port: int
    auth_docker_repo: str
    auth_app_name: str
    auth_local_path: str
    auth_port: int
    jwt_secret: str
    algorithm: str
    access_token_expire_minutes: int

    # gateway
    gateway_docker_repo: str
    gateway_app_name: str
    gateway_port: int
    gateway_local_path: str
    mongo_uri: str
    mongo_port: int

    model_config = SettingsConfigDict(env_file=find_dotenv())


settings = Settings()
