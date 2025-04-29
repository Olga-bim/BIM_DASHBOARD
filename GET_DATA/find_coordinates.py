import os
import fitz
import json
import sqlite3
import re

HUB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "BIMW_-_WXG_Group"))


# 🔹 Выбор проекта
def choose_project():
    projects = [p for p in os.listdir(HUB_PATH) if os.path.isdir(os.path.join(HUB_PATH, p))]
    print("📂 Проекты в хабе:")
    for i, name in enumerate(projects):
        print(f"{i + 1}. {name}")
    selected = int(input("Выберите номер проекта: ")) - 1
    return projects[selected]

# 🔹 Поиск BEP-файла
def find_bep_file(project_path):
    for file in os.listdir(project_path):
        if "BEP" in file.upper() and file.lower().endswith(".pdf"):
            return os.path.join(project_path, file)
    return None

def clean_number(value):
    """Возвращает число как строку с сохранением всех цифр после точки"""
    cleaned = re.sub(r"[^\d\.\-]", "", value.replace(",", ".")).strip()
    return cleaned  # НЕ преобразуем в float!

# 🔹 Извлечение координат
def extract_coordinates(pdf_path):
    doc = fitz.open(pdf_path)
    lines = []
    for page in doc:
        lines.extend(page.get_text("text").splitlines())
    doc.close()

    try:
        ns_index = lines.index("N/S")
        ns = lines[ns_index + 4].strip()
        ew = lines[ns_index + 5].strip()
        elev = lines[ns_index + 6].strip()
        angle = lines[ns_index + 7].strip()

        return {
            "north_south": clean_number(ns),
            "east_west": clean_number(ew),
            "elevation": clean_number(elev),
            "angle_to_true_north": clean_number(angle)
        }

    except Exception as e:
        print("❌ Ошибка при чтении координат:", e)
        return None

# 🔹 Сохранение в JSON
def save_json(project_path, new_data):
    out_path = os.path.join(project_path, "project_coordinates.json")

    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = []

    all_data.append(new_data)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)

    print(f"✅ Добавлено в {out_path}")

# 🔹 Сохранение в SQLite (добавляет таблицу, если её нет, и не дублирует записи)
def save_to_sqlite(project_path, project_name, data):
    db_path = os.path.join(project_path, "project_data.sqlite")

    if not os.path.exists(db_path):
        print("⚠️ База данных не найдена. Она будет создана.")
    else:
        print("ℹ️ Подключение к существующей базе:", db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создание таблицы, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_coordinates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT,
        north_south TEXT,
        east_west TEXT,
        elevation TEXT,
        angle_to_true_north TEXT
    )
    """)

    # Проверка на наличие идентичной записи
    cursor.execute("""
    SELECT 1 FROM project_coordinates
    WHERE project_name = ?
    AND north_south = ?
    AND east_west = ?
    AND elevation = ?
    AND angle_to_true_north = ?
    """, (
        project_name,
        data["north_south"],
        data["east_west"],
        data["elevation"],
        data["angle_to_true_north"]
    ))

    exists = cursor.fetchone()

    if exists:
        print("ℹ️ Эти координаты уже есть в базе. Ничего не добавлено.")
    else:
        cursor.execute("""
        INSERT INTO project_coordinates (
            project_name,
            north_south,
            east_west,
            elevation,
            angle_to_true_north
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            project_name,
            data["north_south"],
            data["east_west"],
            data["elevation"],
            data["angle_to_true_north"]
        ))
        conn.commit()
        print(f"✅ Новые координаты добавлены в базу: {db_path}")

    conn.close()

# 🚀 Основной запуск
def main():
    project_name = choose_project()
    project_path = os.path.join(HUB_PATH, project_name)
    pdf_path = find_bep_file(project_path)

    if not pdf_path:
        print("❌ BEP-файл не найден в проекте.")
        return

    print(f"📄 Найден файл: {pdf_path}")
    coordinates = extract_coordinates(pdf_path)

    if coordinates:
        save_json(project_path, coordinates)
        save_to_sqlite(project_path, project_name, coordinates)

if __name__ == "__main__":
    main()
