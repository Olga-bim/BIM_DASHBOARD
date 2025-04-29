# Используем Node.js 16
FROM node:16

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY frontend/package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем весь frontend
COPY frontend/ .

# Открываем порт для React
EXPOSE 3000

# Команда запуска
CMD ["npm", "start"]
