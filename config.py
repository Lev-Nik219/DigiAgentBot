import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
SCRAPINGDOG_API_KEY = os.getenv("SCRAPINGDOG_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env или переменных окружения")
if not HF_API_TOKEN:
    raise ValueError("HF_API_TOKEN не найден в .env или переменных окружения")
if not SCRAPINGDOG_API_KEY:
    raise ValueError("SCRAPINGDOG_API_KEY не найден в .env или переменных окружения")