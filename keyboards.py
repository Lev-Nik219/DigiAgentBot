from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔍 Анализ переписки")
    builder.button(text="📰 Фактчекинг")
    builder.button(text="🎙 Расшифровка аудио/видео")
    builder.button(text="👪 Мониторинг чатов")
    builder.button(text="📚 Краткое содержание")  # <-- новая кнопка
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Выберите действие")

def cancel_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Нажмите Отмена для выхода")