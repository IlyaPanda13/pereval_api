import os
import json
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.db_params = {
            'host': os.getenv('FSTR_DB_HOST', 'localhost'),
            'port': os.getenv('FSTR_DB_PORT', '5432'),
            'database': os.getenv('FSTR_DB_NAME', 'pereval'),
            'user': os.getenv('FSTR_DB_LOGIN'),
            'password': os.getenv('FSTR_DB_PASS')
        }

    def connect(self):
        """Устанавливаем соединение с БД"""
        try:
            conn = psycopg2.connect(**self.db_params, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            raise

    def add_pereval(self, pereval_data: Dict[str, Any]) -> Optional[int]:
        """
        Добавляет перевал в базу данных
        Возвращает id добавленной записи или None при ошибке
        """
        conn = None
        try:
            raw_data = {
                "beautyTitle": pereval_data.get("beauty_title", ""),
                "title": pereval_data["title"],
                "other_titles": pereval_data.get("other_titles", ""),
                "connect": pereval_data.get("connect", ""),
                "add_time": pereval_data["add_time"],
                "user": {
                    "email": pereval_data["user"]["email"],
                    "phone": pereval_data["user"]["phone"],
                    "fam": pereval_data["user"]["fam"],
                    "name": pereval_data["user"]["name"],
                    "otc": pereval_data["user"].get("otc", "")
                },
                "coords": {
                    "latitude": pereval_data["coords"]["latitude"],
                    "longitude": pereval_data["coords"]["longitude"],
                    "height": pereval_data["coords"]["height"]
                },
                "level": {
                    "winter": pereval_data["level"].get("winter", ""),
                    "summer": pereval_data["level"].get("summer", ""),
                    "autumn": pereval_data["level"].get("autumn", ""),
                    "spring": pereval_data["level"].get("spring", "")
                },
                "status": "new"
            }

            images_list = []
            for img in pereval_data.get("images", []):
                images_list.append({
                    "id": len(images_list) + 1,
                    "title": img["title"]
                })

            images_json = {"images": images_list}

            conn = self.connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO pereval_added (raw_data, images, date_added)
                VALUES (%s::jsonb, %s::jsonb, NOW())
                RETURNING id;
                """

                cursor.execute(query, (json.dumps(raw_data), json.dumps(images_json)))
                pereval_id = cursor.fetchone()['id']

                conn.commit()
                return pereval_id

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Ошибка при добавлении перевала: {e}")
            return None

        finally:
            if conn:
                conn.close()