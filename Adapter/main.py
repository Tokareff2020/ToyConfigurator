import asyncio
import json
import ssl

import aio_pika
import aiohttp

from Worker.config.config import config
from Worker.rabbitmq.channel import AsyncRabbitMQConnection
from Worker.redis.client import get_redis_client


SSL_CONTEXT = ssl.create_default_context(cafile=config.CERT_PATH)


async def process_task(message: aio_pika.IncomingMessage):
    """Обработчик входящих задач из очереди."""
    task_data = json.loads(message.body)
    device_id = task_data.get("equipment_id")
    params = task_data.get("params", "{}")
    redis_client = await get_redis_client()

    async with aiohttp.ClientSession() as session:
        try:
            post_coro = session.post(
                f"{config.SERVICE_A_URL}{device_id}",
                json=params,
                timeout=65,
                ssl=SSL_CONTEXT
            )
            task_data['status'] = 'Task is still running'
            await redis_client.set(task_data.get("id"), json.dumps(task_data))

            async with post_coro as response:
                queue_data = await response.json()
                # Проверяем HTTP статус ответа
                if response.status == 200:
                    task_data['status'] = 'Completed'
                else:
                    task_data['status'] = 'Failed'
                queue_data["task_id"] = task_data.get("id")
                await redis_client.set(task_data.get("id"), json.dumps(task_data))

        except aiohttp.ClientError as e:
            queue_data = {
                "task_id": task_data.get("id"),
                "code": 500,
                "message": f"Ошибка при вызове сервиса A: {str(e)}"
            }
            task_data['status'] = 'Failed'
            await redis_client.set(task_data.get("id"), json.dumps(task_data))

        # Отправка результата в очередь
        await end_task(queue_data)
        result_from_redis = await redis_client.get(task_data.get("id"))
        print(f"Данные из Redis: {result_from_redis}")


async def end_task(result):
    """Отправляет результат выполнения в очередь."""
    channel = await AsyncRabbitMQConnection.get_channel()
    exchange = channel.default_exchange
    message = aio_pika.Message(
        body=json.dumps(result).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )
    await exchange.publish(message, routing_key=config.RESULT_QUEUE)


async def main():
    """Главная асинхронная функция для работы с RabbitMQ."""
    await AsyncRabbitMQConnection.connect()
    await AsyncRabbitMQConnection.consume(process_task)

    try:
        await asyncio.Future()  # Ожидание входящих сообщений
    except KeyboardInterrupt:
        await AsyncRabbitMQConnection.close()


if __name__ == "__main__":
    asyncio.run(main())
