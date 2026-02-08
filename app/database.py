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

    def get_pereval_by_id(self, pereval_id: int):
        """Получить запись перевала по ID"""
        conn = None
        try:
            conn = self.connect()
            with conn.cursor() as cursor:
                query = "SELECT * FROM pereval_added WHERE id = %s"
                cursor.execute(query, (pereval_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Ошибка при получении перевала: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_perevals_by_email(self, email: str):
        """Получить все перевалы по email пользователя"""
        conn = None
        try:
            conn = self.connect()
            with conn.cursor() as cursor:
                query = """
                SELECT * FROM pereval_added 
                WHERE raw_data->'user'->>'email' = %s
                """
                cursor.execute(query, (email,))
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            print(f"Ошибка при поиске по email: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def update_pereval(self, pereval_id: int, update_data: dict):
        """Обновить запись перевала, если статус 'new'"""
        conn = None
        try:
            conn = self.connect()
            with conn.cursor() as cursor:
                check_query = """
                SELECT raw_data->>'status' as status, raw_data->'user' as user_data 
                FROM pereval_added WHERE id = %s
                """
                cursor.execute(check_query, (pereval_id,))
                current = cursor.fetchone()

                if not current:
                    return False, "Запись не найдена"

                if current['status'] != 'new':
                    return False, "Запись нельзя редактировать (статус не 'new')"

                old_user_data = current['user_data']

                new_raw_data = {
                    "beautyTitle": update_data.get("beauty_title", ""),
                    "title": update_data["title"],
                    "other_titles": update_data.get("other_titles", ""),
                    "connect": update_data.get("connect", ""),
                    "add_time": update_data["add_time"],
                    "user": old_user_data,
                    "coords": {
                        "latitude": update_data["coords"]["latitude"],
                        "longitude": update_data["coords"]["longitude"],
                        "height": update_data["coords"]["height"]
                    },
                    "level": {
                        "winter": update_data["level"].get("winter", ""),
                        "summer": update_data["level"].get("summer", ""),
                        "autumn": update_data["level"].get("autumn", ""),
                        "spring": update_data["level"].get("spring", "")
                    },
                    "status": "new"
                }

                images_list = []
                for idx, img in enumerate(update_data.get("images", []), 1):
                    images_list.append({
                        "id": idx,
                        "title": img["title"]
                    })
                images_json = {"images": images_list}

                update_query = """
                UPDATE pereval_added 
                SET raw_data = %s::jsonb, images = %s::jsonb 
                WHERE id = %s AND raw_data->>'status' = 'new'
                RETURNING id
                """

                cursor.execute(update_query,
                               (json.dumps(new_raw_data),
                                json.dumps(images_json),
                                pereval_id))

                if cursor.fetchone():
                    conn.commit()
                    return True, None
                else:
                    return False, "Не удалось обновить запись"

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Ошибка при обновлении перевала: {e}")
            return False, str(e)
        finally:
            if conn:
                conn.close()