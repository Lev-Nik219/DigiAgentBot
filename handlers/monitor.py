import logging
import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from fsm_states import MonitorStates
from keyboards import cancel_kb, main_menu_kb

logger = logging.getLogger(__name__)
router = Router()

monitored_groups = {}

@router.message(F.text == "👪 Мониторинг чатов")
@router.message(Command("monitor"))
async def monitor_start(message: Message, state: FSMContext):
    await state.set_state(MonitorStates.waiting_for_group_id)
    await message.answer(
        "👪 **Мониторинг чатов для родителей**\n\n"
        "Теперь бот будет **молча** следить за всеми сообщениями в указанной группе. "
        "Он анализирует текст на наличие:\n"
        "• признаков буллинга (оскорбления, угрозы);\n"
        "• депрессивных высказываний;\n"
        "• подозрительных ссылок (например, сокращённых).\n\n"
        "Если будет обнаружено что-то тревожное, бот отправит предупреждение **только вам** в личные сообщения. "
        "В группе бот никак себя не проявляет – не отвечает и не ставит реакции.\n\n"
        "**Важно:** чтобы бот мог читать сообщения, он должен быть участником группы. "
        "Для гарантированной доставки всех обновлений рекомендуется назначить его администратором "
        "с минимальными правами (например, только на чтение сообщений).\n\n"
        "Теперь введите ID группы (чата), за которой хотите следить.\n"
        "Как узнать ID группы? Перешлите любое сообщение из группы этому боту в личку — бот покажет ID.",
        reply_markup=cancel_kb()
    )

@router.message(MonitorStates.waiting_for_group_id, F.text)
async def monitor_add_group(message: Message, state: FSMContext):
    try:
        group_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ ID группы должен быть числом. Попробуйте ещё раз или нажмите Отмена.",
                             reply_markup=cancel_kb())
        return

    parent_id = message.from_user.id

    if group_id in monitored_groups:
        if parent_id not in monitored_groups[group_id]:
            monitored_groups[group_id].append(parent_id)
    else:
        monitored_groups[group_id] = [parent_id]

    await message.answer(
        f"✅ Мониторинг группы {group_id} включён. Я буду присылать предупреждения вам в личку.",
        reply_markup=main_menu_kb()
    )
    await state.clear()

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def monitor_group_message(message: Message):
    chat_id = message.chat.id
    if chat_id not in monitored_groups:
        return

    text = message.text or message.caption or ""
    if not text:
        return

    is_dangerous = False
    reason = ""

    bullying_keywords = ["убить", "ненавижу", "тупой", "лох", "дебил", "заткнись"]
    depression_keywords = ["не хочу жить", "самоубийство", "все надоело", "безысходность"]
    dangerous_links = re.findall(r'https?://\S+', text)
    dangerous_sites = ["bit.ly", "tinyurl", "goo.gl", "is.gd"]

    for word in bullying_keywords:
        if word in text.lower():
            is_dangerous = True
            reason = "обнаружены признаки буллинга"
            break
    for word in depression_keywords:
        if word in text.lower():
            is_dangerous = True
            reason = "обнаружены депрессивные высказывания"
            break
    for link in dangerous_links:
        if any(site in link for site in dangerous_sites):
            is_dangerous = True
            reason = "обнаружена подозрительная ссылка"
            break

    if is_dangerous:
        alert = (
            f"⚠️ **Предупреждение** ⚠️\n"
            f"Группа: {chat_id}\n"
            f"Автор: {message.from_user.full_name} (id: {message.from_user.id})\n"
            f"Сообщение: {text}\n"
            f"Причина: {reason}"
        )
        for parent_id in monitored_groups[chat_id]:
            try:
                await message.bot.send_message(parent_id, alert)
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение родителю {parent_id}: {e}")