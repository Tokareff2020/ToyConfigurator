import asyncio

import uvicorn
from fastapi import FastAPI

from ServiceB.config.config import config
from ServiceB.rabbitmq.channel import AsyncRabbitMQConnection
from ServiceB.routes.equipment import eq_router

app = FastAPI()
app.include_router(eq_router)


async def start_rabbitmq():
    await AsyncRabbitMQConnection.connect()


async def start_server():
    server = uvicorn.Server(uvicorn.Config(app, host=config.host, port=config.port))
    await server.serve()


async def main():
    await AsyncRabbitMQConnection.connect()
    task1 = asyncio.create_task(start_rabbitmq())
    task2 = asyncio.create_task(start_server())
    await asyncio.gather(task1, task2)


if __name__ == "__main__":
    asyncio.run(main())
