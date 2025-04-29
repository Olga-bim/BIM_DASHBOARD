# 📊 BIM 360 / ACC Dashboard

**Fullstack стек:** FastAPI (Backend) + React (Frontend)  
**Авторизация:** Autodesk APS (Forge)  
**База данных:** SQLite  
**AI-ассистент:** встроен на основе dataset.csv

---

## 🚀 Быстрый старт

### 1. Клонировать проект
```bash
git clone https://github.com/ТВОЙ_НИК/BIM-DASHBOARD.git
cd BIM-DASHBOARD
2. Установить зависимости
Backend (FastAPI)
bash
Копировать
Редактировать
cd backend
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux
pip install -r requirements.txt
Frontend (React)
bash
Копировать
Редактировать
cd ../frontend
npm install
3. Запустить проект
Backend (FastAPI)
bash
Копировать
Редактировать
cd backend
uvicorn main:app --reload
📍 API будет доступен по адресу: http://127.0.0.1:8000

Frontend (React)
bash
Копировать
Редактировать
cd ../frontend
npm start
📍 Сайт будет доступен по адресу: http://localhost:3000

⚙️ Структура проекта
css
Копировать
Редактировать
WIP_V7/
├── backend/
│   ├── main.py
│   ├── GET_DATA/
│   ├── utils/
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── src/
├── BIMW_-_WXG_Group/
│   ├── Проект1/
│   │   └── project_data.sqlite
│   ├── Проект2/
│   │   └── project_data.sqlite
├── .gitignore
├── README.md
📚 Основные возможности
📁 Получение списка проектов и файлов из BIM 360 / ACC

📄 Таблицы файлов, версий, видов и параметров элементов

🌍 Карта с проектами (координаты, высота, угол)

👷 Управление проектировщиками (добавление, редактирование, удаление)

🧠 Чат-ассистент AI для анализа статуса проектов

📄 Генерация и скачивание PDF-резюме на странице "Обо мне"

📋 Эндпоинты API (FastAPI)

Метод	Endpoint	Описание
GET	/api/token	Получить токен Autodesk
POST	/api/chat	Чат-ассистент по проектным данным
GET	/api/coordinates	Получить координаты всех проектов
GET	/api/designers	Список проектировщиков по проекту
POST	/api/designers	Добавить проектировщика
PUT	/api/designers/{project}/{id}	Обновить проектировщика
DELETE	/api/designers/{project}/{id}	Удалить проектировщика
GET	/api/projects-table	Таблица файлов и версий
GET	/api/views-table	Таблица видов
GET	/api/projects-list	Список проектов
GET	/api/files-by-project	Файлы проекта
GET	/api/views-3d	3D виды моделей
GET	/api/elements-by-view	Элементы и их параметры
🧩 Требования
Python 3.8+

Node.js 18+

npm

FastAPI

Uvicorn

SQLite

React

🔥 Полезные команды

Команда	Описание
uvicorn main:app --reload	Запуск Backend с автоперезагрузкой
npm start	Запуск Frontend
pip freeze > requirements.txt	Обновить список зависимостей
🌐 Основные страницы сайта
🏠 Главная страница (Home) — описание проекта и сохранение новых идей

🙋 Страница "Обо мне" — создание и скачивание PDF-резюме

🗺️ Страница "Карта проектов" — карта с координатами и проектировщиками

🤖 Страница "Чат-ассистент" — AI чат для анализа проектов

📌 Дополнительные замечания
Разрешены все источники (allow_origins=["*"]) для CORS (в продакшене ограничьте).

При запуске сервера обновляется dataset.csv.

Все базы SQLite (project_data.sqlite) находятся в папке BIMW_-_WXG_Group/.

✨ Статус проекта
✅ Получение данных и координат
✅ Управление проектировщиками (CRUD)
✅ Визуализация 3D видов и элементов
✅ AI чат-ассистент
✅ Постоянное развитие и улучшения