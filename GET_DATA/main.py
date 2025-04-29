import asyncio
import aiohttp
import json
import sys
import os
import base64
from get_token import load_token  # Функция для загрузки токена

# ✅ Загружаем access_token
access_token = load_token()

# ✅ Forge API Endpoints
HUBS_ENDPOINT = "https://developer.api.autodesk.com/project/v1/hubs"
PROJECTS_ENDPOINT = "https://developer.api.autodesk.com/project/v1/hubs/{hub_id}/projects"
TOP_FOLDERS_ENDPOINT = "https://developer.api.autodesk.com/project/v1/hubs/{hub_id}/projects/{project_id}/topFolders"
FOLDER_CONTENTS_ENDPOINT = "https://developer.api.autodesk.com/data/v1/projects/{project_id}/folders/{folder_id}/contents"
VERSIONS_ENDPOINT = "https://developer.api.autodesk.com/data/v1/projects/{project_id}/items/{file_id}/versions"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))



# ✅ Кодировка URN в Base64
def encode_urn(urn):
    return base64.b64encode(urn.encode()).decode().rstrip("=")


# ✅ Асинхронный GET-запрос с обработкой 429 (Too Many Requests)
async def fetch(session, url, headers, description):
    for attempt in range(1, 6):
        print(f"🔹 {description} -> {url} (Попытка {attempt})")
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 429:
                print(f"⚠️ Ошибка 429 (Слишком много запросов). Ждём {attempt * 2} сек...")
                await asyncio.sleep(attempt * 2)
            else:
                print(f"❌ Ошибка ({response.status}) при {description}")
                return None
    return None


# ✅ Получение списка хабов
async def get_hubs(session):
    hubs_data = await fetch(session, HUBS_ENDPOINT, {"Authorization": f"Bearer {access_token}"}, "получение списка хабов")
    if hubs_data:
        return [{"id": hub["id"], "name": hub["attributes"]["name"].replace(" ", "_")} for hub in hubs_data.get("data", [])]
    return []


# ✅ Получение списка проектов в хабе
async def get_projects(session, hub_id):
    projects_data = await fetch(session, PROJECTS_ENDPOINT.format(hub_id=hub_id),
                                {"Authorization": f"Bearer {access_token}"}, "получение проектов")
    if projects_data:
        return [{"id": proj["id"], "name": proj["attributes"]["name"].replace(" ", "_")} for proj in
                projects_data.get("data", [])]
    return []


# ✅ Получение корневых папок проекта
async def get_top_folders(session, hub_id, project_id):
    url = TOP_FOLDERS_ENDPOINT.format(hub_id=hub_id, project_id=project_id)
    response = await fetch(session, url, {"Authorization": f"Bearer {access_token}"}, "получение корневых папок")
    return response.get("data", []) if response else []


# ✅ Поиск папки BIM Models внутри Project Files
async def find_bim_models_folder(session, project_id, top_folders):
    for folder in top_folders:
        if "project files" in folder["attributes"]["displayName"].lower():
            project_files_folder_id = folder["id"]
            contents = await fetch(session, FOLDER_CONTENTS_ENDPOINT.format(project_id=project_id, folder_id=project_files_folder_id),
                                   {"Authorization": f"Bearer {access_token}"}, "получение подпапок Project Files")
            if contents:
                for subfolder in contents.get("data", []):
                    if "bim models" in subfolder["attributes"]["displayName"].lower():
                        return subfolder["id"]
    return None


# ✅ Рекурсивный поиск `.rvt` файлов внутри BIM Models
async def get_all_rvt_files(session, project_id, folder_id):
    rvt_files = []
    contents = await fetch(session, FOLDER_CONTENTS_ENDPOINT.format(project_id=project_id, folder_id=folder_id),
                           {"Authorization": f"Bearer {access_token}"}, "поиск файлов Revit")

    if contents:
        for item in contents.get("data", []):
            if item["type"] == "folders":
                rvt_files.extend(await get_all_rvt_files(session, project_id, item["id"]))
            elif item["type"] == "items" and item["attributes"]["displayName"].endswith(".rvt"):
                rvt_files.append({"name": item["attributes"]["displayName"], "id": item["id"]})

    return rvt_files


# ✅ Получение всех версий файла
async def get_file_versions(session, project_id, file_id):
    url = VERSIONS_ENDPOINT.format(project_id=project_id, file_id=file_id)
    response = await fetch(session, url, {"Authorization": f"Bearer {access_token}"}, f"получение версий файла {file_id}")

    versions = []
    if response:
        for version in response.get("data", []):
            attributes = version.get("attributes", {})
            version_data = {
                "version_id": version.get("id", "Неизвестно"),
                "version_number": attributes.get("versionNumber", "Неизвестно"),
                "last_modified_time": attributes.get("lastModifiedTime", "Неизвестно"),
                "last_modified_user": attributes.get("lastModifiedUserName", "Неизвестно"),
                "published_time": attributes.get("publishedTime", "Не опубликовано"),
                "published_user": attributes.get("publishedUserName", "Не опубликовано"),
                "process_state": version.get("extension", {}).get("processState", "Неизвестно"),
                "urn": encode_urn(version["relationships"]["storage"]["data"]["id"])
                if "relationships" in version and "storage" in version["relationships"] else "Нет данных"
            }
            versions.append(version_data)

        return versions
    return []


# ✅ Основная функция обработки проекта
async def process_project(session, hub, project):
    print(f"📂 Обрабатываем проект: {project['name']} (из хаба {hub['name']})")

    # Создаём папку для проекта
    project_path = os.path.join(BASE_DIR, hub["name"], project["name"])
    os.makedirs(project_path, exist_ok=True)

    # Получаем BIM Models
    top_folders = await get_top_folders(session, hub["id"], project["id"])
    bim_models_folder_id = await find_bim_models_folder(session, project["id"], top_folders)

    if not bim_models_folder_id:
        print(f"⚠️ В проекте {project['name']} нет папки 'BIM Models'. Пропускаем...")
        return

    # Получаем файлы Revit
    rvt_files = await get_all_rvt_files(session, project["id"], bim_models_folder_id)
    print(f"📄 Найдено {len(rvt_files)} файлов Revit в {project['name']}.")

    # Получаем версии файлов
    for rvt_file in rvt_files:
        rvt_file["versions"] = await get_file_versions(session, project["id"], rvt_file["id"])

    # Сохраняем rvt_files.json
    json_file_path = os.path.join(project_path, "rvt_files.json")
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump({"project_id": project["id"], "rvt_files": rvt_files}, f, indent=4, ensure_ascii=False)
    print(f"✅ Данные сохранены в {json_file_path}")


# ✅ Основная программа
async def main():
    async with aiohttp.ClientSession() as session:
        hubs = await get_hubs(session)
        while True:
            print("🔹 Доступные хабы:")
            for i, hub in enumerate(hubs, start=1):
                print(f"{i}. {hub['name']}")

            hub_index = int(input("Выберите номер хаба: ")) - 1
            projects = await get_projects(session, hubs[hub_index]["id"])

            print("🔹 Доступные проекты:")
            for i, project in enumerate(projects, start=1):
                print(f"{i}. {project['name']}")

            project_index = int(input("Выберите номер проекта: ")) - 1
            await process_project(session, hubs[hub_index], projects[project_index])

            cont = input("Хотите обработать другой проект? (да/нет): ").strip().lower()
            if cont != "да":
                break


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # 🔹 Исправление ошибки в Windows
    
    asyncio.run(main())  # 🔹 Запуск основного кода