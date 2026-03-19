import aiohttp
import logging
from config import SCRAPINGDOG_API_KEY

logger = logging.getLogger(__name__)

async def search_google(query: str, num_results: int = 5) -> list:
    # Обрезаем запрос, если он слишком длинный (Scrapingdog может не принять)
    if len(query) > 500:
        logger.warning(f"Слишком длинный запрос ({len(query)} символов), обрезаем до 500")
        query = query[:500]

    url = "https://api.scrapingdog.com/google"
    params = {
        "api_key": SCRAPINGDOG_API_KEY,
        "query": query,
        "country": "ru",
        "advance_search": "false"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    logger.error(f"Ошибка Scrapingdog: {resp.status}")
                    if resp.status == 414:
                        logger.error("Запрос слишком длинный, сократите ввод")
                    return []
                data = await resp.json()
                organic = data.get("organic_results", [])
                results = []
                for item in organic[:num_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("url", ""),
                        "snippet": item.get("snippet", "")
                    })
                return results
        except Exception as e:
            logger.error(f"Исключение при запросе к Scrapingdog: {e}")
            return []