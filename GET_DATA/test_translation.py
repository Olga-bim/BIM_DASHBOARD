import asyncio
import aiohttp
import json
import os
import sys
from get_token import load_token  # Загрузка токена из файла

# 🔹 Загружаем access_token
access_token = load_token()

# 🔹 API Endpoints
DERIVATIVE_MANIFEST_ENDPOINT = "https://developer.api.autodesk.com/modelderivative/v2/designdata/{urn}/manifest"

# 🔹 Параметры для ускоренной обработки
BATCH_SIZE = 5  # Количество запросов в одной пачке
semaphore = asyncio.Semaphore(10)  # Ограничение параллельных запросов

# 🔹 Основная папка с хабами и проектами
BASE_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


async def fetch(session, url, headers, description):
    """Асинхронный GET-запрос с обработкой ошибок 429."""
    async with semaphore:
        for attempt in range(1, 6):
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    await asyncio.sleep(attempt * 2)
                else:
                    return None
        return None

async def check_translation_status(session, access_token, urns):
    """Проверяет статус перевода нескольких версий параллельно."""
    tasks = [
        fetch(session, DERIVATIVE_MANIFEST_ENDPOINT.format(urn=urn),
              {"Authorization": f"Bearer {access_token}"}, f"проверка статуса перевода URN {urn}")
        for urn in urns
    ]
    results = await asyncio.gather(*tasks)
    return {urn: (res.get("status") if res else "not available") for urn, res in zip(urns, results)}

async def process_project(session, access_token, hub_name, project_name, project_path):
    """Обрабатывает проект: получает статусы перевода для всех версий."""
    print(f"📂 Обрабатываем проект: {project_name} (из хаба {hub_name})")

    json_path = os.path.join(project_path, "rvt_files.json")
    if not os.path.exists(json_path):
        print(f"⚠️ В проекте {project_name} нет файла rvt_files.json. Пропускаем...")
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        project_data = json.load(f)

    project_id = project_data.get("project_id", "неизвестно")
    print(f"🔹 ID проекта: {project_id}")

    project_results = {}
    
    for rvt_file in project_data.get("rvt_files", []):
        file_name = rvt_file["name"]
        print(f"📄 Проверяем файл: {file_name}")

        versions = rvt_file.get("versions", [])
        urns = [v["urn"] for v in versions if "urn" in v and v["urn"] != "Нет данных"]

        if not urns:
            print(f"⚠️ Нет URN для {file_name}. Перевод невозможен.")
            project_results[file_name] = "Перевод невозможен"
            continue

        # 🔄 Разбиваем на пакеты по BATCH_SIZE
        batch_results = {}
        for i in range(0, len(urns), BATCH_SIZE):
            batch = urns[i:i + BATCH_SIZE]
            statuses = await check_translation_status(session, access_token, batch)

            for version in versions:
                urn = version.get("urn", "Нет данных")
                if urn in statuses:
                    version["translation_status"] = "✅ Переведена" if statuses[urn] == "success" else "⏳ Не переведена"

            batch_results.update(statuses)

        project_results[file_name] = batch_results

    return {
        "project_id": project_id,
        "versions": project_results
    }

async def main():
    """Основная функция для обработки всех проектов в хабах."""
    async with aiohttp.ClientSession() as session:
        hub_folders = [f for f in os.listdir(BASE_FOLDER) if os.path.isdir(os.path.join(BASE_FOLDER, f))]

        print("🔹 Доступные хабы:")
        for idx, hub_name in enumerate(hub_folders, start=1):
            print(f"{idx}. {hub_name}")

        hub_idx = int(input("Выберите номер хаба: ")) - 1
        if hub_idx < 0 or hub_idx >= len(hub_folders):
            print("❌ Ошибка: неверный номер хаба!")
            return

        hub_name = hub_folders[hub_idx]
        hub_path = os.path.join(BASE_FOLDER, hub_name)
        print(f"\n🔹 Выбран хаб: {hub_name}")

        # 🔄 Получаем список проектов внутри хаба
        project_folders = [f for f in os.listdir(hub_path) if os.path.isdir(os.path.join(hub_path, f))]

        print("\n🔹 Доступные проекты:")
        for idx, project_name in enumerate(project_folders, start=1):
            print(f"{idx}. {project_name}")

        project_idx = int(input("Выберите номер проекта: ")) - 1
        if project_idx < 0 or project_idx >= len(project_folders):
            print("❌ Ошибка: неверный номер проекта!")
            return

        project_name = project_folders[project_idx]
        project_path = os.path.join(hub_path, project_name)
        print(f"\n🔹 Выбран проект: {project_name}\n")

        # 🔄 Запускаем обработку проекта
        result = await process_project(session, access_token, hub_name, project_name, project_path)

        if result:
            # 🔄 Сохраняем результаты в JSON
            json_output_path = os.path.join(project_path, "translation_status.json")
            with open(json_output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            print(f"✅ Данные сохранены в {json_output_path}")
        else:
            print(f"⚠️ Обработка проекта {project_name} завершена без данных.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # 🔹 Исправление ошибки в Windows
    
    asyncio.run(main())  # 🔹 Запуск основного кода