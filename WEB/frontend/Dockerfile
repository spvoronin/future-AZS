# --- ЭТАП 1: Сборка проекта ---
FROM node:20-alpine AS build

WORKDIR /app

# Копируем конфиги и устанавливаем зависимости
COPY package*.json ./
RUN npm install

# Копируем весь код фронта
COPY . .

# Собираем проект в оптимизированную папку dist
RUN npm run build

# --- ЭТАП 2: Запуск на Nginx ---
FROM nginx:1.25-alpine

# Копируем сбилженную статику (папку dist) из предыдущего этапа в Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем наш кастомный конфиг Nginx (создадим его следующим шагом)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Запускаем Nginx на переднем плане
CMD ["nginx", "-g", "daemon off;"]