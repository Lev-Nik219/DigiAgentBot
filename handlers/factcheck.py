import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from fsm_states import FactCheckStates
from keyboards import cancel_kb, main_menu_kb
from services.search_service import search_google
from services.huggingface_text import analyze_with_huggingface

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "📰 Фактчекинг")
@router.message(Command("factcheck"))
async def factcheck_start(message: Message, state: FSMContext):
    await state.set_state(FactCheckStates.waiting_for_text_or_url)
    await message.answer(
        "📰 **Фактчекинг новостей**\n\n"
        "Отправьте ссылку на новость или текст новости, которую нужно проверить.\n\n"
        "Я найду первоисточник, проверю дату публикации, поищу опровержения и сообщу, является ли новость достоверной или фейком.\n\n"
        "⏳ Поиск может занять до 20–30 секунд.\n\n"
        "Пожалуйста, отправьте ссылку или текст.",
        reply_markup=cancel_kb()
    )

@router.message(FactCheckStates.waiting_for_text_or_url, F.text)
async def factcheck_process(message: Message, state: FSMContext):
    user_input = message.text.strip()
    await message.answer("⏳ Ищу информацию в интернете... Это может занять до 20 секунд.")

    search_results = await search_google(user_input, num_results=5)

    if not search_results:
        await message.answer("Не удалось найти результаты поиска.", reply_markup=main_menu_kb())
        await state.clear()
        return

    context = "Результаты поиска по запросу:\n"
    for i, res in enumerate(search_results, 1):
        context += f"{i}. {res['title']}\n   {res['snippet']}\n   Ссылка: {res['link']}\n\n"

    prompt = f"""
    Пользователь хочет проверить достоверность следующей новости (или ссылки): {user_input}
    Вот результаты поиска по этой теме:
    {context}
    На основе этих данных определи, является ли новость скорее достоверной, фейковой или требует дополнительной проверки.
    Укажи, есть ли опровержения, противоречия. Если возможно, назови первоисточник.
    Ответ дай на русском языке, понятным для пользователя языком.
    """

    result = await analyze_with_huggingface(prompt)

    if result["success"]:
        await message.answer(result["analysis"], reply_markup=main_menu_kb())
    else:
        await message.answer(f"❌ Ошибка при анализе: {result['error']}", reply_markup=main_menu_kb())

    await state.clear()

@router.message(FactCheckStates.waiting_for_text_or_url)
async def factcheck_wrong_input(message: Message):
    await message.answer("Пожалуйста, отправьте текст или ссылку.", reply_markup=cancel_kb())