from telethon import events, TelegramClient, connection
import os, redis
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
ABH = TelegramClient(
    "BUTTON_BOT",
    api_id,
    api_hash,
    connection=connection.ConnectionTcpFull,
    sequential_updates=False,
    auto_reconnect=True,
    connection_retries=None)
r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True)
