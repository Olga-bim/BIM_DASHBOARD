import sqlite3
import os
import json

def extract_elements(cursor, view_id, objects):
    for obj in objects:
        if isinstance(obj, dict):
            object_id = obj.get("objectid")
            name = obj.get("name")
            raw = json.dumps(obj, ensure_ascii=False)
            cursor.execute("""
                INSERT INTO elements (view_id, object_id, name, raw_json)
                VALUES (?, ?, ?, ?)
            """, (view_id, object_id, name, raw))
            if "objects" in obj:
                extract_elements(cursor, view_id, obj["objects"])

def extract_properties(cursor, view_id, collection):
    for obj in collection:
        if isinstance(obj, dict):
            object_id = obj.get("objectid")
            raw = json.dumps(obj, ensure_ascii=False)
            cursor.execute("""
                INSERT INTO properties (view_id, object_id, raw_json)
                VALUES (?, ?, ?)
            """, (view_id, object_id, raw))


def create_and_fill_sqlite(project_path):
    db_path = os.path.join(project_path, "project_data.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Таблицы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rvt_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            file_name TEXT,
            file_id TEXT,
            version_number INTEGER,
            version_id TEXT,
            urn TEXT,
            last_modified_time TEXT,
            last_modified_user TEXT,
            published_time TEXT,
            published_user TEXT,
            process_state TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            view_key TEXT,
            project_name TEXT,
            file_name TEXT,
            version_number INTEGER,
            view_name TEXT,
            guid TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            view_id INTEGER,
            object_id INTEGER,
            name TEXT,
            raw_json TEXT,
            FOREIGN KEY(view_id) REFERENCES views(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            view_id INTEGER,
            object_id INTEGER,
            raw_json TEXT,
            FOREIGN KEY(view_id) REFERENCES views(id)
        )
    """)

    # rvt_files.json
    rvt_path = os.path.join(project_path, "rvt_files.json")
    if os.path.exists(rvt_path):
        with open(rvt_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            project_id = data.get("project_id")
            for file in data.get("rvt_files", []):
                file_name = file.get("name")
                file_id = file.get("id")
                for version in file.get("versions", []):
                    cursor.execute("""
                        INSERT INTO rvt_files (
                            project_id, file_name, file_id,
                            version_number, version_id, urn,
                            last_modified_time, last_modified_user,
                            published_time, published_user, process_state
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        project_id, file_name, file_id,
                        version.get("version_number"), version.get("version_id"), version.get("urn"),
                        version.get("last_modified_time"), version.get("last_modified_user"),
                        version.get("published_time"), version.get("published_user"), version.get("process_state")
                    ))

    # guids.json
    view_key_to_id = {}
    guids_path = os.path.join(project_path, "guids.json")
    if os.path.exists(guids_path):
        with open(guids_path, "r", encoding="utf-8") as f:
            guids_data = json.load(f)
            for view in guids_data:
                view_key = f"{view['name']}__v{view['version_number']}"
                cursor.execute("""
                    INSERT INTO views (
                        view_key, project_name, file_name,
                        version_number, view_name, guid
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    view_key, view.get("project_name"), view.get("file_name"),
                    view.get("version_number"), view.get("name"), view.get("guid")
                ))
                view_id = cursor.lastrowid
                view_key_to_id[view_key] = view_id

    # metadata.json
    meta_path = os.path.join(project_path, "metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            for view_key, entry in metadata.items():
                view_id = view_key_to_id.get(view_key)
                if not view_id:
                    continue
                objects = entry.get("data", {}).get("data", {}).get("objects", [])
                extract_elements(cursor, view_id, objects)

    # properties.json
    props_path = os.path.join(project_path, "properties.json")
    if os.path.exists(props_path):
        with open(props_path, "r", encoding="utf-8") as f:
            properties = json.load(f)
            for view_key, entry in properties.items():
                view_id = view_key_to_id.get(view_key)
                if not view_id:
                    continue
                collection = entry.get("data", {}).get("data", {}).get("collection", [])
                extract_properties(cursor, view_id, collection)


    conn.commit()
    conn.close()
    return db_path

def main():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    hubs = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]

    print("🔹 Доступные хабы:")
    for i, hub in enumerate(hubs, 1):
        print(f"{i}. {hub}")
    hub_index = int(input("Выберите номер хаба: ")) - 1
    hub_path = os.path.join(base, hubs[hub_index])

    projects = [d for d in os.listdir(hub_path) if os.path.isdir(os.path.join(hub_path, d))]
    print("📁 Доступные проекты:")
    for i, proj in enumerate(projects, 1):
        print(f"{i}. {proj}")
    proj_index = int(input("Выберите номер проекта: ")) - 1
    project_path = os.path.join(hub_path, projects[proj_index])

    print(f"📂 Выбран проект: {projects[proj_index]}")
    db_path = create_and_fill_sqlite(project_path)
    print(f"✅ База данных сохранена: {db_path}")

if __name__ == "__main__":
    main()
