from models import *
from fastapi import FastAPI



app = FastAPI()

@app.post("/tgWebhook")
async def telegram_webhook(update: Update):
    return {
        "status": "ok",
        "data": update,

    }
