import yaml
from pydantic import BaseModel


class Config(BaseModel):
    """Класс для хранения конфигурации"""
    TASK_QUEUE: str
    RESULT_QUEUE: str
    RABBITMQ_HOST: str
    CERT_PATH: str
    SERVICE_A_URL: str
    REDIS_URL: str


try:
    with open('./config/config.yaml', 'r') as file:
        cfg = yaml.safe_load(file)
except FileNotFoundError:
    print('Сonfiguration file was not found, check the correct path.')
    exit()
config = Config(**cfg)
