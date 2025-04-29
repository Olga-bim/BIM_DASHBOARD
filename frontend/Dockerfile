# Этап 1: Сборка React-приложения
FROM node:18 AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Этап 2: Сервер на nginx
FROM nginx:alpine

# Удаляем дефолтную страницу nginx
RUN rm -rf /usr/share/nginx/html/*

# Копируем билд из предыдущего этапа
COPY --from=builder /app/build /usr/share/nginx/html

# Открываем порт 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
