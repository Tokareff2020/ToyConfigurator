import time

from fastapi import APIRouter, HTTPException

from ServiceA.config.config import config
from ServiceA.models import CfgParams
from ServiceA.utils import is_correct_id

eq_router = APIRouter(prefix="/api/v1/equipment/cpe", tags=["Equipment"])


@eq_router.post("/{id}")
def configure_device(id: str, params: CfgParams):
    if not is_correct_id(id):
        raise HTTPException(status_code=404, detail="The requested equipment is not found")
    if params.username != config.username or params.password != config.password:
        raise HTTPException(status_code=401, detail="Wrong username or password")
    if params.timeoutInSeconds > 60:
        raise HTTPException(status_code=500, detail="Internal provisioning exception")
    time.sleep(params.timeoutInSeconds)

    return {"code": 200, "message": f"success"}
