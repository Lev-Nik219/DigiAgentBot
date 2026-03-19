from aiogram.fsm.state import StatesGroup, State

class AnalysisStates(StatesGroup):
    """Состояния для анализа переписки."""
    waiting_for_text = State()

class FactCheckStates(StatesGroup):
    """Состояния для фактчекинга."""
    waiting_for_text_or_url = State()

class TranscribeStates(StatesGroup):
    """Состояния для расшифровки аудио/видео."""
    waiting_for_media = State()

class MonitorStates(StatesGroup):
    """Состояния для мониторинга чатов."""
    waiting_for_group_id = State()

class SummarizeStates(StatesGroup):
    """Состояния для создания краткого содержания."""
    waiting_for_text = State()