import os
import asyncio
import logging
import subprocess
from pathlib import Path
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError, TelegramNetworkError, TelegramRetryAfter

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 МБ (лимит Telegram Bot API)

async def download_file_from_message(message: Message, retries: int = 2) -> str:
    # Определяем тип файла и получаем file_id
    if message.photo:
        file_id = message.photo[-1].file_id
        file_ext = ".jpg"
    elif message.audio:
        file_id = message.audio.file_id
        file_ext = ".mp3"
    elif message.video:
        file_id = message.video.file_id
        file_ext = ".mp4"
    elif message.voice:
        file_id = message.voice.file_id
        file_ext = ".ogg"
    elif message.document:
        file_id = message.document.file_id
        file_ext = os.path.splitext(message.document.file_name)[1] if message.document.file_name else ".bin"
    elif message.video_note:
        file_id = message.video_note.file_id
        file_ext = ".mp4"
    else:
        raise ValueError("Неподдерживаемый тип медиа")

    try:
        file = await message.bot.get_file(file_id)
        logger.info(f"Информация о файле: {file.file_path}, размер: {file.file_size} байт")
    except Exception as e:
        logger.error(f"Ошибка get_file: {e}")
        raise Exception(f"Не удалось получить информацию о файле: {e}")

    if file.file_size and file.file_size > MAX_FILE_SIZE:
        size_mb = file.file_size / (1024 * 1024)
        raise Exception(f"Файл слишком большой ({size_mb:.1f} МБ). Максимум {MAX_FILE_SIZE/1024/1024:.0f} МБ.")

    destination = TEMP_DIR / f"{file_id}{file_ext}"

    for attempt in range(retries):
        try:
            await message.bot.download_file(file.file_path, destination)
            logger.info(f"Файл скачан: {destination}")
            return str(destination)
        except asyncio.TimeoutError:
            logger.warning(f"Таймаут при скачивании (попытка {attempt+1}/{retries})")
            if attempt == retries - 1:
                raise Exception("Таймаут при скачивании. Проверьте соединение и попробуйте позже.")
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Ошибка скачивания: {e}")
            raise Exception(f"Ошибка скачивания: {e}")

    raise Exception("Неизвестная ошибка при скачивании")

async def cleanup_file(file_path: str):
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Файл удалён: {file_path}")
    except Exception as e:
        logger.warning(f"Не удалось удалить {file_path}: {e}")

def get_audio_duration(file_path: str) -> float:
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        logger.warning(f"Не удалось получить длительность файла: {e}")
        return 0.0