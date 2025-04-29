📊 BIM 360 / ACC Dashboard
Fullstack стек: FastAPI (Backend) + React (Frontend)
Авторизация: Autodesk APS (Forge)
База данных: SQLite
AI-ассистент: встроен (на основе dataset.csv)

🚀 Быстрый старт (локально)
1. Клонировать проект
bash
Копировать
Редактировать
git clone https://github.com/ТВОЙ_НИК/BIM-DASHBOARD.git
cd BIM-DASHBOARD
2. Установить зависимости
Backend (FastAPI):

bash
Копировать
Редактировать
cd backend
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux
pip install -r requirements.txt
Frontend (React):

bash
Копировать
Редактировать
cd ../frontend
npm install
3. Запустить проект локально
Backend (FastAPI):

bash
Копировать
Редактировать
cd backend
uvicorn main:app --reload
📍 API будет доступен на: http://127.0.0.1:8000

Frontend (React):

bash
Копировать
Редактировать
cd ../frontend
npm start
📍 Сайт будет доступен на: http://localhost:3000

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
│   ├── .env
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

📋 Основные эндпоинты API (FastAPI)

Метод	Endpoint	Описание
GET	/api/token	Получить токен Autodesk
POST	/api/chat	Чат-ассистент по проектным данным
GET	/api/coordinates	Получить координаты всех проектов
GET	/api/designers	Получить проектировщиков проекта
POST	/api/designers	Добавить проектировщика
PUT	/api/designers/{project}/{id}	Обновить проектировщика
DELETE	/api/designers/{project}/{id}	Удалить проектировщика
GET	/api/projects-table	Таблица файлов и версий
GET	/api/views-table	Таблица видов
GET	/api/projects-list	Список проектов
GET	/api/files-by-project	Файлы проекта
GET	/api/views-3d	3D виды моделей
GET	/api/elements-by-view	Элементы и их параметры
🌐 Основные страницы сайта (Frontend)

Страница	Описание
🏠 Home	Главная страница, описание проекта и блок идей
🙋 About	Создание и скачивание PDF-резюме
📁 Project	Раздел со всеми подстраницами проекта
🗺️ Project → Map	Карта координат проектов и проектировщики
📋 Project → Projects Table	Таблица файлов и версий
📂 Project → Views Table	Таблица видов (GUIDs) и Forge Viewer
🧱 Project → Elements Table	Таблица элементов и параметров
🤖 Project → AI Assistant	AI чат-ассистент по проектам
🧩 Требования для запуска локально
Python 3.8+

Node.js 18+

npm

FastAPI

Uvicorn

SQLite

React

🔥 Полезные команды

Команда	Описание
uvicorn main:app --reload	Запуск Backend (FastAPI)
npm start	Запуск Frontend (React)
pip freeze > requirements.txt	Обновить зависимости Python
📌 Замечания
CORS разрешён для всех источников (allow_origins=["*"]). В продакшене рекомендуется ограничить.

Базы данных SQLite (project_data.sqlite) лежат в папке BIMW_-_WXG_Group/.

Фронтенд автоматически берёт URL бекенда из .env файла.

✨ Статус проекта
✅ Получение данных и координат проектов

✅ CRUD проектировщиков

✅ Отображение 3D видов Revit через Forge

✅ Таблицы файлов, версий и элементов

✅ AI чат-ассистент по проектным данным

✅ Постоянное развитие и оптимизация