import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from fsm_states import SummarizeStates
from keyboards import cancel_kb, main_menu_kb
from services.huggingface_text import analyze_with_huggingface

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "📚 Краткое содержание")
@router.message(Command("summarize"))
async def summarize_start(message: Message, state: FSMContext):
    await state.set_state(SummarizeStates.waiting_for_text)
    await message.answer(
        "📚 **Краткое содержание**\n\n"
        "Отправьте длинный текст (статью, новость, лекцию, главу книги), и я создам краткое изложение с ключевыми мыслями.\n\n"
        "**Что вы получите:**\n"
        "• сжатый пересказ основного содержания\n"
        "• выделение главных идей и выводов\n"
        "• сохранение важных деталей\n\n"
        "⏳ Время обработки зависит от объёма текста и может занимать до 30 секунд.\n\n"
        "Пожалуйста, отправьте текст для анализа.",
        reply_markup=cancel_kb()
    )

@router.message(SummarizeStates.waiting_for_text, F.text)
async def summarize_process(message: Message, state: FSMContext):
    text = message.text
    await message.answer("⏳ Составляю краткое содержание... Это может занять до 30 секунд.")

    prompt = f"Составь краткое содержание следующего текста. Выдели основные идеи, ключевые моменты и выводы. Используй русский язык.\n\nТекст:\n{text}\n\nКраткое содержание:"

    result = await analyze_with_huggingface(prompt)

    if result["success"]:
        summary = result["analysis"]
        if not summary or len(summary) < 20:
            await message.answer("❌ Не удалось создать краткое содержание. Попробуйте другой текст.", reply_markup=main_menu_kb())
        else:
            await message.answer(summary, reply_markup=main_menu_kb())
    else:
        await message.answer(f"❌ Ошибка: {result['error']}", reply_markup=main_menu_kb())

    await state.clear()

@router.message(SummarizeStates.waiting_for_text)
async def summarize_wrong_input(message: Message):
    await message.answer("Пожалуйста, отправьте текстовое сообщение.", reply_markup=cancel_kb())