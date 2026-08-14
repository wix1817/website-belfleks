#!/bin/bash
# Скрипт первоначальной настройки для развертывания Astro + PocketBase в LXC

set -e

echo "Обновление системы..."
apt-get update && apt-get upgrade -y

echo "Установка зависимостей (Docker, Node.js, Python)..."
apt-get install -y ca-certificates curl gnupg python3 python3-pip python3-venv

# Установка Docker
if ! command -v docker &> /dev/null; then
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

# Установка Node.js (для сборки Astro, если собирается на сервере, но лучше использовать Docker multistage build)
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

echo "Подготовка структуры папок..."
mkdir -p pocketbase/pb_data
mkdir -p pocketbase/pb_public
chmod -R 777 pocketbase/

echo "Запуск Docker Compose..."
docker compose up -d --build

echo "Готово! Astro и PocketBase запущены."
echo "Astro: http://127.0.0.1:3000"
echo "PocketBase Admin: http://127.0.0.1:8090/_/"
