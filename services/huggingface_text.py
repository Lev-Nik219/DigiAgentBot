import asyncio
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None
_pipeline = None
_model_name = "Qwen/Qwen2.5-1.5B-Instruct"
_max_length = 2048

def get_text_pipeline():
    global _pipeline, _model, _tokenizer
    if _pipeline is None:
        logger.info(f"⏳ Загрузка модели {_model_name}...")
        _tokenizer = AutoTokenizer.from_pretrained(_model_name)
        _model = AutoModelForCausalLM.from_pretrained(_model_name)
        # Убираем max_new_tokens из pipeline, будем передавать при вызове
        _pipeline = pipeline(
            "text-generation",
            model=_model,
            tokenizer=_tokenizer,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=True
        )
        logger.info("✅ Модель загружена.")
    return _pipeline, _tokenizer

def truncate_prompt(prompt: str, tokenizer, max_length: int) -> str:
    tokens = tokenizer.encode(prompt, truncation=True, max_length=max_length)
    return tokenizer.decode(tokens, skip_special_tokens=True)

async def analyze_with_huggingface(prompt: str, max_new_tokens: int = 500) -> dict:
    pipe, tokenizer = get_text_pipeline()
    loop = asyncio.get_running_loop()

    messages = [
        {"role": "system", "content": "Ты — эксперт по психологии общения. Всегда отвечай на русском языке строго по заданному пользователем формату. Не добавляй лишних комментариев."},
        {"role": "user", "content": prompt}
    ]
    formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    truncated_prompt = truncate_prompt(formatted_prompt, tokenizer, _max_length - 100)

    def _generate():
        # Передаём max_new_tokens только здесь
        result = pipe(truncated_prompt, max_new_tokens=max_new_tokens)
        generated = result[0]['generated_text']
        if generated.startswith(truncated_prompt):
            generated = generated[len(truncated_prompt):].strip()
        return generated

    try:
        result = await loop.run_in_executor(None, _generate)
        return {"success": True, "analysis": result}
    except Exception as e:
        logger.exception("Ошибка при генерации текста")
        return {"success": False, "error": str(e)}