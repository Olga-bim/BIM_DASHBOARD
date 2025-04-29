import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
HUB_FOLDER = os.path.join(BASE_DIR, "BIMW_-_WXG_Group")
DATASET_PATH = os.path.join(BASE_DIR, "backend", "data", "dataset.csv")

def run_dataset_update():
    all_data = []

    for project in os.listdir(HUB_FOLDER):
        print(f"\n🔍 Проект: {project}")
        db_path = os.path.join(HUB_FOLDER, project, "project_data.sqlite")

        if not os.path.isfile(db_path):
            print("⚠️ Нет файла project_data.sqlite")
            continue

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Получаем список таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]
            print(f"📋 Таблицы: {tables}")

            for table in tables:
                if table.startswith("sqlite_"):
                    continue  # системные таблицы

                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                print(f"🔸 Таблица {table}: столбцы {columns}")

                try:
                    df_table = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                    df_table.insert(0, "project", project)
                    df_table.insert(1, "table_name", table)
                    all_data.append(df_table)
                except Exception as e:
                    print(f"❌ Ошибка при чтении таблицы {table}: {e}")

        except Exception as e:
            print(f"❌ Ошибка в {project}: {e}")
        finally:
            conn.close()

    if all_data:
        df_final = pd.concat(all_data, ignore_index=True)
        os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
        df_final.to_csv(DATASET_PATH, index=False)
        print(f"\n✅ dataset.csv обновлён: {len(df_final)} строк")
    else:
        print("\n⚠️ Нет данных для сохранения")
