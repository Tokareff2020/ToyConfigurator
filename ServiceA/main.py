import uvicorn
from fastapi import FastAPI

from ServiceA.config.config import config
from ServiceA.routes.equipment import eq_router

if __name__ == "__main__":
    app = FastAPI()
    app.include_router(eq_router)
    uvicorn.run(app, host=config.host, port=config.port,
                ssl_keyfile="../certificates/server.key", ssl_certfile="../certificates/server.crt")
