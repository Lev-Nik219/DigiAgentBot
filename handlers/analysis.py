import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from fsm_states import AnalysisStates
from keyboards import cancel_kb, main_menu_kb
from services.huggingface_text import analyze_with_huggingface

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "🔍 Анализ переписки")
@router.message(Command("analyze"))
async def analysis_start(message: Message, state: FSMContext):
    await state.set_state(AnalysisStates.waiting_for_text)
    await message.answer(
        "🔍 **Анализ переписки**\n\n"
        "Отправьте текст (диалог, сообщение или несколько сообщений), который вы хотите проанализировать.\n\n"
        "Бот проанализирует текст на наличие:\n"
        "• манипуляций\n"
        "• пассивной агрессии\n"
        "• скрытых оскорблений\n\n"
        "Определит общую тональность (позитивная, нейтральная, негативная, агрессивная).\n"
        "Если будут найдены манипуляции, объяснит их суть.\n"
        "Предложит 2–3 варианта ответа, которые помогут парировать манипуляцию или выйти из конфликта.\n\n"
        "⏳ Ожидание ответа может занять до 30 секунд.",
        reply_markup=cancel_kb()
    )

@router.message(AnalysisStates.waiting_for_text, F.text)
async def analysis_process_text(message: Message, state: FSMContext):
    text = message.text
    await message.answer("⏳ Начинаю анализ... Это может занять до 30 секунд.")

    prompt = f"""Проанализируй следующий диалог на наличие манипуляций, пассивной агрессии, скрытых оскорблений. Определи общую тональность (позитивная, нейтральная, негативная, агрессивная). Если найдены манипуляции, объясни их суть. Предложи 2-3 варианта ответа, которые помогут парировать манипуляцию или выйти из конфликта.

Диалог: {text}

Твой ответ должен строго соответствовать следующему примеру:

Тональность: [позитивная/нейтральная/негативная/агрессивная]
Манипуляции: [опишите, какие манипуляции или агрессия обнаружены, если есть; если нет, напишите "не обнаружены"]
Варианты ответа:
1. [первый вариант]
2. [второй вариант]
3. [третий вариант (необязательно)]

Важно: отвечай только по делу, не добавляй лишнего текста. Используй русский язык."""

    result = await analyze_with_huggingface(prompt)

    if result["success"]:
        analysis = result["analysis"]
        if not analysis or len(analysis) < 20:
            await message.answer("❌ Не удалось получить содержательный анализ. Попробуйте ещё раз.", reply_markup=main_menu_kb())
        else:
            await message.answer(analysis, reply_markup=main_menu_kb())
    else:
        await message.answer(f"❌ Ошибка: {result['error']}", reply_markup=main_menu_kb())

    await state.clear()

@router.message(AnalysisStates.waiting_for_text)
async def analysis_wrong_input(message: Message):
    await message.answer("Пожалуйста, отправьте текстовое сообщение.", reply_markup=cancel_kb())