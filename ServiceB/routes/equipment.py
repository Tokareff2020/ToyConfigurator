import asyncio
import json
import re
import time
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException

from ServiceA.models import CfgParams
from ServiceB.config.config import config
from ServiceB.rabbitmq.channel import AsyncRabbitMQConnection
from ServiceB.redis.client import get_redis_client

eq_router = APIRouter(prefix="/api/v1/equipment/cpe", tags=["Equipment"])


@eq_router.post("/{id}")
async def create_config_task(id: str, params: CfgParams):
    if not id.isalnum() or len(id) < 6:
        raise HTTPException(status_code=400, detail="Invalid device ID")

    task_id = str(uuid.uuid4())
    task_data = {
        "timestamp": datetime.now().timestamp(),
        "id": task_id,
        "equipment_id": id,
        "params": params.model_dump(),
        "status": "pending"
    }

    task_json = json.dumps(task_data)

    redis_client = await get_redis_client()
    await redis_client.set(task_id, task_json)

    await AsyncRabbitMQConnection.publish_message(config.TASK_QUEUE, task_data)

    return {"code": 200, "taskId": task_id}


@eq_router.get("/{id}/task/{task}")
async def get_task_status(id: str, task: str):
    if not re.fullmatch(r"^[a-zA-Z0-9]{6,}$", id):
        raise HTTPException(status_code=404, detail="The requested equipment is not found")

    redis_client = await get_redis_client()
    task_data = await redis_client.get(task)

    if task_data:
        task_json = json.loads(task_data)
        status = task_json.get("status", "")
        if status == "Task is still running":
            return {"code": 204, "message": status}
        elif status in ("Completed", "Failed"):
            return {"code": 200, "message": status}
        else:
            raise HTTPException(status_code=500, detail="Internal provisioning exception")
    else:
        channel = await AsyncRabbitMQConnection.get_channel()
        results_queue = await channel.declare_queue("config_results", durable=True)

        # Пытаемся в течение 5 секунд найти сообщение с нужным task_id
        start = time.time()
        found_result = None
        while time.time() - start < 5:
            try:
                msg = await results_queue.get(timeout=1, no_ack=False)
                result_json = json.loads(msg.body)
                if result_json.get("task_id") == task:
                    found_result = result_json
                    await msg.ack()
                    break
                else:
                    # Если сообщение не соответствует, возвращаем его в очередь
                    await msg.nack(requeue=True)
            except asyncio.TimeoutError:
                continue

        if found_result is not None:
            # Если сообщение найдено, добавляем предупреждение о проблемах с Redis
            found_result["redis_warning"] = "Redis was down; result retrieved from RabbitMQ."
            return {
                "code": 200,
                "message": found_result.get("status", "Unknown"),
                "details": found_result
            }
        else:
            raise HTTPException(status_code=404, detail="The requested task is not found")

