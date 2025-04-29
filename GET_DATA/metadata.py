import os
import json
import asyncio
import aiohttp
import requests
from get_token import get_access_token
import sys

if sys.platform.startswith('win') and sys.version_info < (3, 10):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def get_all_view_guids(access_token, urn, save_path, project_name, file_name, version_number):
    url = f"https://developer.api.autodesk.com/modelderivative/v2/designdata/{urn}/metadata"
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"🔍 Получаем список видов для URN: {urn} ...")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        raw_views = response.json().get("data", {}).get("metadata", [])
        views = []
        for view in raw_views:
            view.update({
                "project_name": project_name,
                "file_name": file_name,
                "version_number": version_number
            })
            views.append(view)

        path = os.path.join(save_path, "guids.json")
        existing = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)

        existing_guids = {v["guid"] for v in existing}
        for view in views:
            if view["guid"] not in existing_guids:
                existing.append(view)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=4, ensure_ascii=False)

        print(f"✅ Виды сохранены ({len(views)} новых)")
        return {v["guid"]: v["name"] for v in views}
    else:
        print(f"❌ Ошибка получения видов: {response.status_code}")
        return {}

async def get_metadata_for_view(session, access_token, urn, guid, semaphore):
    url = f"https://developer.api.autodesk.com/modelderivative/v2/designdata/{urn}/metadata/{guid}"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with semaphore:
        async with session.get(url, headers=headers) as resp:
            return await resp.json() if resp.status == 200 else None

async def get_properties_for_view(session, access_token, urn, guid, semaphore):
    url = f"https://developer.api.autodesk.com/modelderivative/v2/designdata/{urn}/metadata/{guid}/properties"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with semaphore:
        async with session.get(url, headers=headers) as resp:
            return await resp.json() if resp.status == 200 else None

def make_unique_view_key(view_name, version_number):
    return f"{view_name}__v{version_number}"

async def process_all_views(access_token, urn, project_path, guid_name_map, version_number, project_name, file_name):
    metadata_result = {}
    properties_result = {}
    semaphore = asyncio.Semaphore(5)

    async with aiohttp.ClientSession() as session:
        metadata_list = await asyncio.gather(*[
            get_metadata_for_view(session, access_token, urn, guid, semaphore)
            for guid in guid_name_map
        ])
        for guid, metadata in zip(guid_name_map, metadata_list):
            if metadata:
                view_name = guid_name_map[guid]
                key = make_unique_view_key(view_name, version_number)
                metadata_result[key] = {
                    "project_name": project_name,
                    "file_name": file_name,
                    "version_number": version_number,
                    "view_name": view_name,
                    "data": metadata
                }

        properties_list = await asyncio.gather(*[
            get_properties_for_view(session, access_token, urn, guid, semaphore)
            for guid in guid_name_map
        ])
        for guid, props in zip(guid_name_map, properties_list):
            if props:
                view_name = guid_name_map[guid]
                key = make_unique_view_key(view_name, version_number)
                properties_result[key] = {
                    "project_name": project_name,
                    "file_name": file_name,
                    "version_number": version_number,
                    "view_name": view_name,
                    "data": props
                }

    def merge_json(path, new_data):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                old = json.load(f)
        else:
            old = {}
        old.update(new_data)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(old, f, indent=4, ensure_ascii=False)

    merge_json(os.path.join(project_path, "metadata.json"), metadata_result)
    merge_json(os.path.join(project_path, "properties.json"), properties_result)
    print("🎉 metadata и properties обновлены!")

async def main():
    base_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "BIMW_-_WXG_Group"))

    projects = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]

    for i, proj in enumerate(projects, 1):
        print(f"{i}. {proj}")
    selected = int(input("Выберите номер проекта: ")) - 1
    project_name = projects[selected]
    project_path = os.path.join(base_folder, project_name)

    rvt_file_path = os.path.join(project_path, "rvt_files.json")
    if not os.path.exists(rvt_file_path):
        print("❌ rvt_files.json не найден в проекте.")
        return

    with open(rvt_file_path, "r", encoding="utf-8") as f:
        rvt_data = json.load(f)

    access_token = get_access_token()

    # Обходим все файлы и все версии
    for file in rvt_data.get("rvt_files", []):
        file_name = file.get("name")
        for version in file.get("versions", []):
            urn = version.get("urn", "").strip()
            version_number = version.get("version_number")

            if not urn:
                continue

            print(f"🔹 Обработка файла: {file_name}, версия: {version_number}")

            guid_map = get_all_view_guids(access_token, urn, project_path, project_name, file_name, version_number)
            if not guid_map:
                print(f"⚠️ Нет видов для версии {version_number}")
                continue

            await process_all_views(access_token, urn, project_path, guid_map, version_number, project_name, file_name)

if __name__ == "__main__":
    asyncio.run(main())
