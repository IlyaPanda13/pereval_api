from fastapi import FastAPI, HTTPException, Query
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


@app.get("/submitData/{pereval_id}")
async def get_pereval(pereval_id: int):
    """
    Получить информацию о перевале по ID
    """
    try:
        pereval = db_manager.get_pereval_by_id(pereval_id)

        if not pereval:
            raise HTTPException(
                status_code=404,
                detail="Перевал не найден"
            )

        if pereval.get('date_added'):
            pereval['date_added'] = pereval['date_added'].isoformat()

        return pereval

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)}"
        )


@app.patch("/submitData/{pereval_id}")
async def update_pereval(pereval_id: int, pereval_update: PerevalData):
    """
    Обновить информацию о перевале (только если статус 'new')
    """
    try:
        update_data = pereval_update.dict()

        success, message = db_manager.update_pereval(pereval_id, update_data)

        if success:
            return {"state": 1, "message": None}
        else:
            return {"state": 0, "message": message}

    except Exception as e:
        return {"state": 0, "message": f"Ошибка: {str(e)}"}


@app.get("/submitData/")
async def get_perevals_by_email(user__email: str = Query(..., description="Email пользователя")):
    """
    Получить все перевалы, отправленные пользователем с указанным email
    """
    try:
        perevals = db_manager.get_perevals_by_email(user__email)

        # Преобразуем даты в строках
        for pereval in perevals:
            if pereval.get('date_added'):
                pereval['date_added'] = pereval['date_added'].isoformat()

        return {
            "count": len(perevals),
            "results": perevals
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)}"
        )