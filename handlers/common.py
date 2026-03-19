import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards import main_menu_kb, cancel_kb

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я DigiAgent — ваш помощник в цифровых задачах.\n"
        "Выберите нужную функцию из меню ниже:",
        reply_markup=main_menu_kb()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Я умею:\n"
        "🔍 Анализ переписки – определю манипуляции.\n"
        "📰 Фактчекинг – проверю новость.\n"
        "🎙 Расшифровка аудио/видео – переведу речь в текст.\n"
        "👪 Мониторинг чатов – для родителей.\n"
        "📄 Реставрация документов – улучшу фото и распознаю текст.",
        reply_markup=main_menu_kb()
    )

@router.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активного действия.", reply_markup=main_menu_kb())
        return
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_menu_kb())