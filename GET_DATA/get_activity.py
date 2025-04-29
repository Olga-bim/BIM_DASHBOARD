import os
import json
import asyncio
import aiohttp
from get_token import load_token


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Загружаем access_token из файла
access_token = load_token()

HUBS_ENDPOINT = "https://developer.api.autodesk.com/project/v1/hubs"
ACTIVITY_LOG_BIM360 = "https://developer.api.autodesk.com/bim360/admin/v1/projects/{}/activity-stream"
ACTIVITY_LOG_ACC = "https://developer.api.autodesk.com/construction/admin/v1/projects/{}/activity-stream"


async def fetch(session, url, headers, description):
    """Асинхронный GET-запрос с обработкой ошибок."""
    for attempt in range(1, 6):
        print(f"🔹 {description} -> {url} (Попытка {attempt})")
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                print(f"✅ Успешно: {description}")
                return await response.json()
            elif response.status == 429:
                print(f"⚠️ Ошибка 429 (Слишком много запросов). Ждем {attempt * 2} секунд...")
                await asyncio.sleep(attempt * 2)
            else:
                print(f"❌ Ошибка ({response.status}) при {description}")
                return None
    return None


# Получение аккаунт ID для хаба
async def get_hub_account_id(session, access_token):
    """Получает `account_id` для хаба."""
    response = await fetch(session, HUBS_ENDPOINT, {"Authorization": f"Bearer {access_token}"}, "получение списка хабов")
    if response and "data" in response:
        # Выбираем первый хаб
        hub = response["data"][0]
        hub_name = hub["attributes"]["name"]
        account_id = hub["id"]
        print(f"✅ Найден `account_id`: {account_id} для хаба {hub_name}")
        return account_id, hub_name
    else:
        print(f"❌ Ошибка: не удалось получить хабы.")
        return None, None


# Получение списка проектов в хабе по ID хаба
async def get_projects(session, access_token, hub_id):
    """Получает список всех проектов в хабе."""
    url = f"https://developer.api.autodesk.com/project/v1/hubs/{hub_id}/projects"
    return await fetch(session, url, {"Authorization": f"Bearer {access_token}"}, "получение проектов")


# Получение активности для каждого проекта
async def get_activity_logs(session, access_token, project_id):
    """Получает журнал активности для проекта."""
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    url_bim360 = ACTIVITY_LOG_BIM360.format(project_id)
    url_acc = ACTIVITY_LOG_ACC.format(project_id)

    # Пробуем получить активность сначала для BIM 360, потом для ACC
    response_bim360 = await fetch(session, url_bim360, headers, f"получение активности (BIM 360) для проекта {project_id}")
    if not response_bim360:
        response_bim360 = await fetch(session, url_acc, headers, f"получение активности (ACC) для проекта {project_id}")

    return response_bim360 or {"data": []}  # если активности нет, возвращаем пустой JSON


# Сохранение активности в проект
async def save_activity_logs(project_folder, activity_logs):
    """Сохраняет журнал активности в файл JSON внутри папки проекта."""
    json_file_path = os.path.join(project_folder, "activity_logs.json")

    # Если папка проекта не найдена, выводим ошибку
    if not os.path.exists(project_folder):
        print(f"❌ Папка проекта {project_folder} не найдена. Пропуск.")
        return

    print(f"🔍 Путь для сохранения: {json_file_path}")  # Для отладки
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(activity_logs, f, indent=4, ensure_ascii=False)

    print(f"✅ Данные активности для проекта сохранены в {json_file_path}")


# Основной процесс обработки проекта
async def process_project(session, access_token, hub_name, project):
    """Обрабатывает проект: получает и сохраняет активность."""
    project_folder = os.path.join(BASE_DIR, hub_name, project["attributes"]["name"])
  # Папка с проектом
    print(f"🔍 Папка проекта: {project_folder}")  # Для отладки

    # Получение активности для проекта
    activity_logs = await get_activity_logs(session, access_token, project["id"])

    # Сохранение данных активности в файл
    await save_activity_logs(project_folder, activity_logs)


# Основной процесс
async def main():
    async with aiohttp.ClientSession() as session:
        account_id, hub_name = await get_hub_account_id(session, access_token)
        if account_id and hub_name:
            projects = await get_projects(session, access_token, account_id)
            for project in projects["data"]:
                await process_project(session, access_token, hub_name, project)
        print("🎉 Все проекты успешно обработаны!")


if __name__ == "__main__":
    asyncio.run(main())
