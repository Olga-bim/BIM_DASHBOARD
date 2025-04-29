# Используем легкий nginx-образ
FROM nginx:alpine

# Копируем production-билд внутрь контейнера
COPY build/ /usr/share/nginx/html

# Открываем 80 порт для nginx
EXPOSE 80
