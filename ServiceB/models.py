from typing import Optional

from pydantic import BaseModel


class CfgParams(BaseModel):
    timeoutInSeconds: Optional[int] = 60
    username: str
    password: str
    vlan: Optional[int]
    interfaces: list[int]
