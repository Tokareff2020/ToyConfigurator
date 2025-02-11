import json

import aio_pika


class AsyncRabbitMQConnection:
    _rabbitmq_url = "amqp://guest:guest@localhost/"
    _connection = None
    _channel = None

    @classmethod
    async def connect(cls):
        """
        Устанавливает соединение с RabbitMQ и открывает канал,
        если они ещё не установлены или закрыты.
        """
        if cls._connection is None or cls._connection.is_closed:
            cls._connection = await aio_pika.connect_robust(cls._rabbitmq_url)
        if cls._channel is None or cls._channel.is_closed:
            cls._channel = await cls._connection.channel()
            await cls._channel.set_qos(prefetch_count=1)

    @classmethod
    async def get_channel(cls):
        """
        Возвращает открытый канал. Если канал закрыт – переподключается.
        """
        if cls._channel is None or cls._channel.is_closed:
            await cls.connect()
        return cls._channel

    @classmethod
    async def publish_message(cls, queue_name: str, message: dict):
        """
        Публикует сообщение в указанную очередь.
        Если канал закрыт, происходит переподключение.
        """
        channel = await cls.get_channel()
        if channel.is_closed:
            raise RuntimeError("Канал закрыт, не могу отправить сообщение.")

        # Объявляем очередь (если она не существует, она будет создана)
        await channel.declare_queue(queue_name, durable=True)
        message_body = json.dumps(message).encode()

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT  # Делает сообщение стойким
            ),
            routing_key=queue_name
        )

    @classmethod
    async def get_rabbitmq_conn(cls):
        """
        Возвращает открытый канал RabbitMQ после проверки подключения.
        """
        await cls.connect()
        return await cls.get_channel()

    @classmethod
    async def close(cls):
        """
        Закрывает соединение с RabbitMQ, если оно открыто.
        """
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
