from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from GET_DATA.get_token import get_access_token


from fastapi.responses import JSONResponse
from collections import defaultdict
import os
import sqlite3
from pyproj import Transformer
from math import isnan, isinf
from fastapi import Path, Body
from pydantic import BaseModel, field_validator, EmailStr
from pydantic import field_validator


import re

from pydantic import BaseModel

from dotenv import load_dotenv

import pandas as pd

# # Импорт функций генерации и обучения
# from backend.utils.generate_dataset import run_dataset_update




app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Можно заменить на ["http://localhost:3000"] для безопасности
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 📁 Путь к хабу
HUB_PATH = r"C:\WXG\Projects\WIP_V7\BIMW_-_WXG_Group"

# 🌍 Трансформация координат
transformer = Transformer.from_crs("EPSG:2039", "EPSG:4326", always_xy=True)

# Загружаем переменные окружения
load_dotenv()


# 🔹 Модель проектировщика
class Designer(BaseModel):
    project_name: str
    discipline: str
    first_name: str
    last_name: str
    company: str
    email: EmailStr
    phone: str
    position: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        pattern = re.compile(r"^\+?\d[\d\s\-]{7,}$")
        if not pattern.match(value):
            raise ValueError("Некорректный номер телефона")
        return value
    


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
HUB_FOLDER = os.path.join(BASE_DIR, "..", "BIMW_-_WXG_Group")

@app.get("/api/token")
def get_token():
    token = get_access_token()
    return {"access_token": token}

# 🔹 Эндпоинт: координаты проектов
@app.get("/api/coordinates")
def get_coordinates():
    all_data = []

    for project_name in os.listdir(HUB_PATH):
        project_path = os.path.join(HUB_PATH, project_name)
        db_path = os.path.join(project_path, "project_data.sqlite")
        if not os.path.exists(db_path):
            continue

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT project_name, north_south, east_west, elevation, angle_to_true_north
                FROM project_coordinates
            """)
            rows = cursor.fetchall()

            for row in rows:
                try:
                    ns = float(str(row[1]).replace(",", "."))
                    ew = float(str(row[2]).replace(",", "."))
                    if ns > 1_000_000:
                        ns = ns / 100
                    if ew > 1_000_000:
                        ew = ew / 100
                    lon, lat = transformer.transform(ew, ns)

                    if any([isnan(lat), isinf(lat), isnan(lon), isinf(lon)]):
                        continue

                    all_data.append({
                        "project": row[0],
                        "latitude": lat,
                        "longitude": lon,
                        "elevation": row[3],
                        "angle": row[4],
                    })

                except Exception:
                    continue
            conn.close()

        except Exception:
            continue

    return all_data

# 🔹 Эндпоинт: получить проектировщиков проекта
@app.get("/api/designers")
def get_designers(project: str):
    db_path = os.path.join(HUB_PATH, project, "project_data.sqlite")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="База данных не найдена")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_designers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            discipline TEXT,
            first_name TEXT,
            last_name TEXT,
            company TEXT,
            email TEXT,
            phone TEXT,
            position TEXT
        )
    """)
    conn.commit()

    cursor.execute("""
        SELECT id, discipline, first_name, last_name, company, email, phone, position

        FROM project_designers
        WHERE project_name = ?
    """, (project,))
    rows = cursor.fetchall()
    conn.close()

    return [
    {
        "id": row[0],
        "discipline": row[1],
        "first_name": row[2],
        "last_name": row[3],
        "company": row[4],
        "email": row[5],
        "phone": row[6],
        "position": row[7],
    }
    for row in rows
]

# 🔹 Эндпоинт: добавить проектировщика
@app.post("/api/designers")
def add_designer(designer: Designer):
    db_path = os.path.join(HUB_PATH, designer.project_name, "project_data.sqlite")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="База данных не найдена")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_designers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            discipline TEXT,
            first_name TEXT,
            last_name TEXT,
            company TEXT,
            email TEXT,
            phone TEXT,
            position TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO project_designers (
            project_name, discipline, first_name, last_name,
            company, email, phone, position
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        designer.project_name,
        designer.discipline,
        designer.first_name,
        designer.last_name,
        designer.company,
        designer.email,
        designer.phone,
        designer.position
    ))
    conn.commit()
    conn.close()
    return {"status": "✅ Участник добавлен"}


@app.put("/api/designers/{project}/{id}")
def update_designer(
    project: str,
    id: int,
    updated_data: Designer
):
    db_path = os.path.join(HUB_PATH, project, "project_data.sqlite")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="База данных не найдена")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Обновляем данные, исключив проверку project_name в WHERE
    cursor.execute("""
        UPDATE project_designers SET
            discipline = ?, first_name = ?, last_name = ?,
            company = ?, email = ?, phone = ?, position = ?
        WHERE id = ?
    """, (
        updated_data.discipline,
        updated_data.first_name,
        updated_data.last_name,
        updated_data.company,
        updated_data.email,
        updated_data.phone,
        updated_data.position,
        id
    ))

    conn.commit()
    conn.close()
    return {"status": "✅ Проектировщик обновлён"}

@app.delete("/api/designers/{project}/{id}")
def delete_designer(project: str, id: int):
    db_path = os.path.join(HUB_PATH, project, "project_data.sqlite")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="База данных не найдена")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM project_designers
        WHERE id = ? AND project_name = ?
    """, (id, project))
    conn.commit()
    conn.close()

    return {"status": f"🗑 Проектировщик с ID {id} удалён из проекта {project}"}

@app.get("/api/projects-table")
def get_projects_table():
    results = []
    for project_name in os.listdir(HUB_PATH):
        project_path = os.path.join(HUB_PATH, project_name)
        db_path = os.path.join(project_path, "project_data.sqlite")
        if not os.path.exists(db_path):
            continue

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT file_name, version_number, last_modified_time,
                       last_modified_user, published_time, published_user, process_state
                FROM rvt_files
            """)
            rows = cursor.fetchall()

            for row in rows:
                results.append({
                    "project": project_name,
                    "file_name": row[0],
                    "version_number": row[1],
                    "last_modified_time": row[2],
                    "last_modified_user": row[3],
                    "published_time": row[4],
                    "published_user": row[5],
                    "process_state": row[6]
                })
        except Exception as e:
            print(f"❌ Ошибка в {project_name}: {e}")
        finally:
            conn.close()

    return results


@app.get("/api/views-table")
def get_views_table():
    from collections import defaultdict

    result = []
    for project_name in os.listdir(HUB_PATH):
        project_path = os.path.join(HUB_PATH, project_name)
        db_path = os.path.join(project_path, "project_data.sqlite")
        if not os.path.exists(db_path):
            continue

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT project_name, file_name, version_number, view_name, guid
                FROM views
            """)
            rows = cursor.fetchall()
            conn.close()

            structure = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
            for row in rows:
                project, file_name, version, view_name, guid = row
                discipline = "Неизвестно"
                for part in file_name.split("_"):
                    if part.upper() in ["AR", "ST", "MEP", "EL", "HVAC", "SAN", "COORD"]:
                        discipline = part.upper()
                structure[discipline][file_name][version].append({
                    "view_name": view_name,
                    "guid": guid
                })

            for discipline, files in structure.items():
                for file_name, versions in files.items():
                    for version, views in versions.items():
                        result.append({
                            "project": project_name,
                            "discipline": discipline,
                            "file_name": file_name,
                            "version_number": version,
                            "views": views
                        })

        except Exception as e:
            print(f"❌ Ошибка в {project_name}: {e}")

    return result

# 🔧 Удобная функция для многослойной структуры
def nested_dict():
    return defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

@app.get("/api/projects-list")
def get_projects_list():
    return [p for p in os.listdir(HUB_PATH) if os.path.isdir(os.path.join(HUB_PATH, p))]

@app.get("/api/files-by-project")
def get_files_by_project(project: str):
    db_path = os.path.join(HUB_PATH, project, "project_data.sqlite")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="База данных не найдена")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT file_name FROM views")
    files = [row[0] for row in cursor.fetchall()]
    conn.close()
    return files

@app.get("/api/views-3d")
def get_views_3d(project: str, file_name: str):
    db_path = os.path.join(HUB_PATH, project, "project_data.sqlite")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="База данных не найдена")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT view_name, version_number, guid FROM views
        WHERE file_name = ? AND role = '3d'
    """, (file_name,))
    views = [{"view_name": v[0], "version_number": v[1], "guid": v[2]} for v in cursor.fetchall()]
    conn.close()
    return views

@app.get("/api/elements-by-view")
def get_elements_by_view(project: str, file_name: str, version: int, view_name: str):
    db_path = os.path.join(HUB_PATH, project, "project_data.sqlite")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="База данных не найдена")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT v.id
        FROM views v
        WHERE v.project_name = ? AND v.file_name = ? AND v.version_number = ? AND v.view_name = ?
    """, (project, file_name, version, view_name))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return []

    view_id = row[0]

    cursor.execute("""
        SELECT e.object_id, e.name, e.raw_json, p.raw_json
        FROM elements e
        LEFT JOIN properties p
        ON e.view_id = p.view_id AND e.object_id = p.object_id
        WHERE e.view_id = ?
    """, (view_id,))
    elements = []
    for obj_id, name, el_raw, prop_raw in cursor.fetchall():
        try:
            el_json = json.loads(el_raw) if el_raw else {}
        except:
            el_json = {}
        try:
            prop_json = json.loads(prop_raw) if prop_raw else {}
        except:
            prop_json = {}

        elements.append({
            "object_id": obj_id,
            "name": name,
            "element_data": el_json,
            "properties": prop_json
        })

    conn.close()
    return elements

@app.post("/api/chat")
async def chat_assistant(request: Request):
    body = await request.json()
    question = body.get("question", "").lower().strip()

    if not os.path.exists(DATASET_PATH):
        return {"answer": "🤖 Ассистент временно недоступен, так как база данных AI не загружена."}


# @app.post("/api/chat")
# async def chat_assistant(request: Request):
#     body = await request.json()
#     question = body.get("question", "").lower().strip()

#     if not os.path.exists(DATASET_PATH):
#         return {"answer": "⚠️ dataset.csv не найден."}

#     try:
#         df = pd.read_csv(DATASET_PATH)
#     except Exception as e:
#         return {"answer": f"⚠️ Ошибка при чтении данных: {e}"}

#     # Все проекты и таблицы
#     all_projects = set(os.listdir(HUB_FOLDER))
#     dataset_projects = set(df["project"].dropna().unique()) if "project" in df.columns else set()
#     table_names = df["table_name"].unique() if "table_name" in df.columns else []
#     missing_projects = all_projects - dataset_projects

#     # -------------------------------- КООРДИНАТЫ --------------------------------
#     coord_keywords = ["coord", "north", "east", "lat", "lon", "n/s", "e/w", "геолокац", "местоположен", "где", "координат", "расположен", "находится"]
#     if any(k in question for k in coord_keywords):
#         # ищем любые столбцы с координатами
#         coord_cols = [col for col in df.columns if any(kw in col.lower() for kw in coord_keywords)]

#         if not coord_cols:
#             return {"answer": "⚠️ Не найдены поля, похожие на координаты."}

#         sample = df[["project"] + coord_cols].dropna().head(5).to_dict(orient="records")
#         rows = [
#             f"📍 {r['project']}: " + ", ".join([f"{k}={r[k]}" for k in coord_cols if pd.notna(r.get(k))])
#             for r in sample
#         ]
#         return {"answer": f"🗺️ Примеры координат:\n" + "\n".join(rows)}

#     # -------------------------------- НАЗВАНИЯ ПРОЕКТОВ --------------------------------
#     if any(k in question for k in ["назв", "перечисли", "список", "что у меня", "покажи проекты", "какие проекты"]):
#         if dataset_projects:
#             return {"answer": f"📁 Проекты: {', '.join(sorted(dataset_projects))}"}
#         return {"answer": "⚠️ В dataset нет проектов."}

#     # -------------------------------- СКОЛЬКО ПРОЕКТОВ --------------------------------
#     if "сколько" in question and "проект" in question:
#         return {"answer": f"📊 Всего проектов в dataset: {len(dataset_projects)}"}

#     # -------------------------------- ПРОПУЩЕННЫЕ ПРОЕКТЫ --------------------------------
#     if any(k in question for k in ["почему", "не загружен", "отсутств", "пропущен", "только"]):
#         if missing_projects:
#             return {"answer": f"⚠️ Пропущенные проекты: {', '.join(sorted(missing_projects))}"}
#         return {"answer": "✅ Все проекты были успешно загружены."}

#     # -------------------------------- ТАБЛИЦЫ --------------------------------
#     if any(k in question for k in ["таблиц", "table", "какие таблицы", "что есть"]):
#         return {"answer": f"📋 Таблицы: {', '.join(sorted(table_names))}"}

#     # -------------------------------- ДИСЦИПЛИНЫ --------------------------------
#     if any(k in question for k in ["дисциплин", "discipline", "раздел", "инженер"]):
#         if "discipline" in df.columns and "table_name" in df.columns:
#             rvt_df = df[df["table_name"] == "rvt_files"]
#             disciplines = rvt_df["discipline"].dropna().unique()
#             return {"answer": f"🛠 Дисциплины: {', '.join(sorted(disciplines))}"}
#         else:
#             return {"answer": "⚠️ В dataset нет таблицы 'rvt_files' или столбца 'discipline'."}


#     # -------------------------------- ГОРОДА --------------------------------
#     if "город" in question:
#         city_cols = [col for col in df.columns if "city" in col.lower()]
#         if city_cols:
#             cities = df[city_cols[0]].dropna().unique()
#             return {"answer": f"🏙️ Города: {', '.join(sorted(cities))}"}
#         return {"answer": "⚠️ Столбец 'city' не найден."}

#     # -------------------------------- ВЕРСИИ --------------------------------
#     if "верси" in question:
#         if "version_count" in df.columns:
#             total = df["version_count"].sum()
#             return {"answer": f"🔁 Всего версий: {int(total)}"}
#         return {"answer": "⚠️ В dataset нет данных по версиям."}

#     # -------------------------------- ДАТЫ --------------------------------
#     if any(k in question for k in ["дата", "период", "время", "года"]):
#         if "first_version" in df.columns and "last_version" in df.columns:
#             min_date = pd.to_datetime(df["first_version"], errors="coerce").min().date()
#             max_date = pd.to_datetime(df["last_version"], errors="coerce").max().date()
#             return {"answer": f"📅 Данные от {min_date} до {max_date}"}
#         return {"answer": "⚠️ В dataset нет информации о датах версий."}

#     # -------------------------------- ПО УМОЛЧАНИЮ --------------------------------
#     return {
#         "answer": (
#             "🤖 Я понимаю вопросы о проектах, координатах, дисциплинах, таблицах, городах, версиях и датах.\n"
#             "Попробуй: 'Где находятся проекты?', 'Какие дисциплины?', 'Сколько версий?', 'Какие таблицы есть?'"
#         )
#     }


# @app.on_event("startup")
# def startup_tasks():
#     print("🚀 Инициализация ассистента...")
#     run_dataset_update()
#     print("✅ dataset.csv обновлён и готов для анализа.")


