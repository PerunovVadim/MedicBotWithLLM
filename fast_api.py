import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from medic_bot import MedicBotCore
from llm_service import LLMService
from gca import GigaChatAdapter
from config import CONFIG
from datetime import datetime, timezone
import time

app = FastAPI()
SYSTEM_PROMPT = """Вы — Ассистент регистратуры поликлиники Читинской Государственной Медицинской Академии. Ваша задача — отвечать ТОЛЬКО на вопросы, связанные с записью к врачу, медицинскими услугами и работой поликлиники. Не отклоняйтесь от темы.
            Ответ должен быть сформулирован в виде текста, а не JSON.
            Правила:

                Тематика:

                    Запись на прием (к врачу, на диагностику, анализы).

                    Режим работы поликлиники и врачей.

                    Неотложная помощь (куда обратиться).

                    Правила подготовки к процедурам.

                Запрещено:

                    Давать медицинские консультации (например, интерпретировать симптомы, назначать лечение).

                    Отвечать на вопросы не по теме (погода, политика, IT и т.д.).

                Тон:

                    Вежливый, четкий, без лишней информации.
                    """
llm_service = LLMService(
    adapter=GigaChatAdapter(
        system_prompt=SYSTEM_PROMPT,
        credentials=CONFIG["SBER_AUTH"]

    )
)
bot_core = MedicBotCore(llm_service)

class QARequest(BaseModel):
    question: str
    temperature: float = 0.7
    max_length: int = 500
    top_k: int = 3
    confidence_threshold: float = 0.5

@app.get("/health")
async def health_check():
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"status": "ok", "timestamp": current_time}

@app.post("/qa")
async def qa_endpoint(request: QARequest):
    try:
        # Фиксируем время начала обработки
        start_time = time.time()

        # Выполняем основную логику (например, получение ответа от бота)
        answer = await bot_core.get_answer(request.question,
                                           temperature=request.temperature,
                                           max_length=request.max_length,
                                           top_k=request.top_k,
                                           confidence_threshold=request.confidence_threshold)

        # Фиксируем время окончания обработки
        end_time = time.time()

        # Вычисляем время обработки
        processing_time = round(end_time - start_time, 2)  # В секундах, округленное до 2 знаков

        return {
            "answer": answer,
            "links": [],
            "request_id": str(uuid.uuid4()),
            "processing_time": processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "code": 500})

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"error": exc.detail["error"], "code": exc.detail["code"]}