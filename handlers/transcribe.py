import logging
from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from fsm_states import TranscribeStates
from keyboards import cancel_kb, main_menu_kb
from services.huggingface_asr import transcribe_audio
from services.mindmap_service import generate_mindmap
from utils.helpers import download_file_from_message, cleanup_file, get_audio_duration

logger = logging.getLogger(__name__)
router = Router()

MAX_MESSAGE_LENGTH = 4000

def split_text(text: str, max_len: int = MAX_MESSAGE_LENGTH):
    parts = []
    while len(text) > max_len:
        split_pos = text.rfind(' ', 0, max_len)
        if split_pos == -1:
            split_pos = max_len
        parts.append(text[:split_pos].strip())
        text = text[split_pos:].strip()
    if text:
        parts.append(text)
    return parts

@router.message(F.text == "🎙 Расшифровка аудио/видео")
@router.message(Command("transcribe"))
async def transcribe_start(message: Message, state: FSMContext):
    await state.set_state(TranscribeStates.waiting_for_media)
    await message.answer(
        "🎙 **Расшифровка аудио и видео**\n\n"
        "Отправьте аудио или видео файл (лекция, подкаст, голосовое сообщение, видеосообщение).\n\n"
        "Я расшифрую речь в текст и выделю ключевые тезисы.\n\n"
        "**Поддерживаемые форматы:**\n"
        "• аудио (mp3, m4a, ogg и др.)\n"
        "• видео (mp4, mov и др.)\n"
        "• голосовые сообщения\n"
        "• видеосообщения (кружки)\n\n"
        "⏳ Время обработки зависит от длительности файла. Для файла длительностью 1 минута – примерно 30–50 секунд.",
        reply_markup=cancel_kb()
    )

@router.message(
    StateFilter(TranscribeStates.waiting_for_media),
    F.content_type.in_({
        ContentType.AUDIO,
        ContentType.VIDEO,
        ContentType.VOICE,
        ContentType.DOCUMENT,
        ContentType.VIDEO_NOTE
    })
)
async def transcribe_process_media(message: Message, state: FSMContext):
    logger.info(f"Получен медиафайл, тип: {message.content_type}")

    try:
        file_path = await download_file_from_message(message)
        logger.info(f"Файл скачан: {file_path}")
    except Exception as e:
        error_text = str(e) if str(e) else "Неизвестная ошибка"
        logger.error(f"Ошибка скачивания файла: {repr(e)}")
        await message.answer(f"❌ Не удалось скачать файл: {error_text}", reply_markup=main_menu_kb())
        await state.clear()
        return

    duration = get_audio_duration(file_path)
    if duration > 0:
        estimated_seconds = int(duration * 0.8)
        minutes = estimated_seconds // 60
        seconds = estimated_seconds % 60
        time_msg = f"⏳ Файл длительностью {int(duration//60)} мин {int(duration%60)} сек.\n"
        time_msg += f"Примерное время обработки: {minutes} мин {seconds} сек."
        await message.answer(time_msg)
    else:
        await message.answer("⏳ Начинаю расшифровку... (невозможно оценить время)")

    try:
        transcript = await transcribe_audio(file_path)
        if not transcript:
            await message.answer("❌ Не удалось распознать речь.", reply_markup=main_menu_kb())
            await state.clear()
            return

        mindmap = await generate_mindmap(transcript)

        transcript_parts = split_text(transcript)
        total_parts = len(transcript_parts)
        for i, part in enumerate(transcript_parts, 1):
            header = f"📝 **Расшифровка (часть {i}/{total_parts}):**\n\n" if total_parts > 1 else "📝 **Расшифровка:**\n\n"
            await message.answer(header + part, parse_mode="Markdown")

        await message.answer(f"📌 **Ключевые тезисы:**\n{mindmap}", parse_mode="Markdown", reply_markup=main_menu_kb())

    except Exception as e:
        logger.error(f"Ошибка обработки: {repr(e)}", exc_info=True)
        error_message = str(e) if str(e) else "Неизвестная ошибка"
        if len(error_message) > 200:
            error_message = error_message[:200] + "..."
        await message.answer(f"❌ Ошибка при обработке: {error_message}", reply_markup=main_menu_kb())
    finally:
        await cleanup_file(file_path)
        await state.clear()

@router.message(StateFilter(TranscribeStates.waiting_for_media))
async def transcribe_wrong_input(message: Message):
    logger.warning(f"Неподходящий тип ввода в состоянии waiting_for_media: {message.content_type}")
    await message.answer(
        "Пожалуйста, отправьте аудио или видео файл (поддерживаются: аудио, видео, голосовые, видеосообщения, документы).",
        reply_markup=cancel_kb()
    )