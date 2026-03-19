async def generate_mindmap(text: str) -> str:
    lines = text.split('.')
    points = [line.strip() for line in lines if len(line.strip()) > 20][:5]
    mindmap = "Ключевые тезисы:\n"
    for i, point in enumerate(points, 1):
        mindmap += f"{i}. {point}\n"
    return mindmap
