import asyncio  
import aiohttp
import json
import os
import sys
import time
from get_token import load_token  # 🔹 Загружаем токен без нового запроса
# === Глобальные переменные ===
BASE_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "BIMW_-_WXG_Group"))
  # Папка хаба
VERSION_STATUS_FILE = "versions_status.json"  # Файл со статусами версий

# === Загружаем токен ===
access_token = load_token()

# === API эндпоинты ===
DERIVATIVE_MANIFEST_ENDPOINT = "https://developer.api.autodesk.com/modelderivative/v2/designdata/{urn}/manifest"

# === Асинхронный GET-запрос ===
async def fetch(session, url, headers, description):
    """Асинхронный GET-запрос с обработкой ошибок 429."""
    for attempt in range(1, 6):
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 429:
                print(f"⚠️ Ошибка 429 ({description}), ждём {attempt * 2} сек...")
                await asyncio.sleep(attempt * 2)
            else:
                print(f"❌ Ошибка {response.status} ({description})")
                return None
    return None

# === Проверка статуса перевода ===
async def check_translation_status(session, urn):
    """Проверяет статус перевода версии."""
    url = DERIVATIVE_MANIFEST_ENDPOINT.format(urn=urn)
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await fetch(session, url, headers, f"Статус перевода URN {urn}")
    if response:
        return response.get("status", "not available")
    return "not available"

# === Выбор проекта ===
def select_project():
    """Выбирает проект из доступных папок в хабе."""
    projects = [f for f in os.listdir(BASE_FOLDER) if os.path.isdir(os.path.join(BASE_FOLDER, f))]

    if not projects:
        print("❌ В хабе нет проектов.")
        return None

    print("🔹 Доступные проекты:")
    for i, project in enumerate(projects, start=1):
        print(f"{i}. {project}")

    choice = int(input("Выберите номер проекта: ")) - 1
    if 0 <= choice < len(projects):
        return projects[choice]
    return None

# === Обработка проекта ===
async def process_project(project_name):
    """Обрабатывает проект, проверяя статусы всех версий."""
    project_path = os.path.join(BASE_FOLDER, project_name)
    json_path = os.path.join(project_path, "rvt_files.json")

    if not os.path.exists(json_path):
        print(f"⚠️ В проекте {project_name} нет файла rvt_files.json. Пропускаем...")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        project_data = json.load(f)

    versions_data = {}  # Сюда запишем статусы версий

    async with aiohttp.ClientSession() as session:
        for rvt_file in project_data.get("rvt_files", []):
            file_name = rvt_file["name"]
            versions_data[file_name] = []

            for version in rvt_file.get("versions", []):
                version_number = version["version_number"]
                urn = version.get("urn", "Нет данных")

                if urn == "Нет данных":
                    print(f"⚠️ Версия {version_number} ({file_name}) - URN отсутствует, перевод невозможен.")
                    versions_data[file_name].append({"version": version_number, "status": "Перевод невозможен", "urn": "Нет данных"})
                    continue

                status = await check_translation_status(session, urn)
                print(f"✅ Версия {version_number} ({file_name}) - {status}")
                versions_data[file_name].append({"version": version_number, "status": status, "urn": urn})

    # === Сохранение в JSON ===
    save_versions_status(project_name, versions_data)

# === Сохранение в JSON ===
def save_versions_status(project_name, versions_data):
    """Сохраняет данные о версиях в versions_status.json"""
    if os.path.exists(VERSION_STATUS_FILE):
        with open(VERSION_STATUS_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = {}

    if "BIMW_-_WXG_Group" not in all_data:
        all_data["BIMW_-_WXG_Group"] = {}

    all_data["BIMW_-_WXG_Group"][project_name] = versions_data

    with open(VERSION_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print(f"📂 Данные сохранены в {VERSION_STATUS_FILE}")

# === Основная функция ===
async def main():
    project_name = select_project()
    if not project_name:
        return

    print(f"📂 Обрабатываем проект: {project_name} (из хаба BIMW_-_WXG_Group)")
    await process_project(project_name)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # 🔹 Исправление ошибки в Windows
    
    asyncio.run(main())  # 🔹 Запуск основного кода
