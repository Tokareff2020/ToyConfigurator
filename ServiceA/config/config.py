import yaml
from pydantic import BaseModel


class Config(BaseModel):
    """Класс для хранения конфигурации"""
    username: str
    password: str
    host: str
    port: int


try:
    with open('config/config.yaml', 'r') as file:
        cfg = yaml.safe_load(file)
except FileNotFoundError:
    print('Сonfiguration file was not found, check the correct path.')
    exit()
config = Config(**cfg)
