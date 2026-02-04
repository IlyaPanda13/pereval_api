from fastapi import FastAPI, HTTPException
from app.models import PerevalData
from app.database import DatabaseManager
from typing import Dict, Any

app = FastAPI(title="Pereval API", description="API для добавления перевалов")

db_manager = DatabaseManager()


@app.post("/submitData")
async def submit_data(pereval: PerevalData) -> Dict[str, Any]:
    """
    Метод для добавления нового перевала

    Принимает JSON с данными о перевале
    Возвращает JSON с результатом операции
    """
    try:
        pereval_dict = pereval.dict()

        pereval_id = db_manager.add_pereval(pereval_dict)

        if pereval_id is None:
            return {
                "status": 500,
                "message": "Ошибка при сохранении данных в базу данных",
                "id": None
            }

        return {
            "status": 200,
            "message": None,
            "id": pereval_id
        }

    except Exception as e:
        return {
            "status": 500,
            "message": f"Внутренняя ошибка сервера: {str(e)}",
            "id": None
        }


@app.get("/")
async def root():
    return {"message": "Pereval API работает!"}