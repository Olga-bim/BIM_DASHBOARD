import os
import sqlite3

# 🔹 Пути
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def choose_hub():
    hubs = [d for d in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, d))]
    print("📂 Хабы:")
    for i, h in enumerate(hubs, 1):
        print(f"{i}. {h}")
    selected = int(input("Выберите номер хаба: ")) - 1
    return os.path.join(BASE_PATH, hubs[selected])

def choose_project(hub_path):
    projects = [p for p in os.listdir(hub_path) if os.path.isdir(os.path.join(hub_path, p))]
    print("\n📁 Проекты:")
    for i, name in enumerate(projects, 1):
        print(f"{i}. {name}")
    selected = int(input("Выберите номер проекта: ")) - 1
    return projects[selected], os.path.join(hub_path, projects[selected])

def create_table(db_path):
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
    conn.close()
    print("✅ Таблица project_designers готова.")

def get_discipline():
    options = [
        "Архитектура", "Конструкция", "Инсталляция",
        "Кондиционирование", "Электрика", "Пневматика", "Спринклеры", "Другое"
    ]
    print("\nВыберите дисциплину:")
    for i, d in enumerate(options, 1):
        print(f"{i}. {d}")
    selected = int(input("Введите номер дисциплины: ")) - 1
    if selected == 7:
        return input("Введите название дисциплины: ").strip()
    return options[selected]

def add_designer(db_path, project_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    discipline = get_discipline()
    first_name = input("Имя: ").strip()
    last_name = input("Фамилия: ").strip()
    company = input("Фирма: ").strip()
    email = input("Email: ").strip()
    phone = input("Телефон: ").strip()
    position = input("Должность: ").strip()

    cursor.execute("""
    INSERT INTO project_designers (
        project_name, discipline, first_name, last_name,
        company, email, phone, position
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        project_name, discipline, first_name, last_name,
        company, email, phone, position
    ))

    conn.commit()
    conn.close()
    print("✅ Участник добавлен!")

# 🚀 Основной запуск
def main():
    hub_path = choose_hub()
    project_name, project_path = choose_project(hub_path)
    db_path = os.path.join(project_path, "project_data.sqlite")

    if not os.path.exists(db_path):
        open(db_path, "w").close()

    create_table(db_path)

    while True:
        add = input("Добавить участника? (y/n): ").strip().lower()
        if add != "y":
            break
        add_designer(db_path, project_name)

if __name__ == "__main__":
    main()
