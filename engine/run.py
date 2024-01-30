import os
from dotenv import load_dotenv
from engine.bot import client
from engine.logger import init_logger

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')


def run_discord_bot():
    init_logger()
    client.run(DISCORD_BOT_TOKEN)
