import asyncio
import logging
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

# Ленивая инициализация модели (загружается при первом вызове)
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        logger.info("⏳ Загрузка модели Whisper (faster-whisper)... Это может занять время при первом запуске.")
        # Используем модель 'small' (баланс скорости и качества)
        # device='cpu', compute_type='int8' для экономии памяти
        _whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
        logger.info("✅ Модель загружена.")
    return _whisper_model

async def transcribe_audio(file_path: str) -> str:
    """
    Транскрибация аудио с использованием локальной модели faster-whisper.
    Запускается в отдельном потоке, чтобы не блокировать asyncio.
    """
    model = get_whisper_model()
    loop = asyncio.get_running_loop()

    def _transcribe():
        # Можно указать язык для повышения точности (например, 'ru')
        segments, info = model.transcribe(file_path, language="ru", task="transcribe", beam_size=5)
        text = " ".join([segment.text for segment in segments])
        return text

    try:
        text = await loop.run_in_executor(None, _transcribe)
        return text
    except Exception as e:
        logger.exception("Ошибка при распознавании через faster-whisper")
        raise Exception(f"Ошибка распознавания: {e}")