#!/usr/bin/env bash
# скачиваем uv и запускаем команду установки зависимостей
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
# Postgres позволяет подключиться к удаленной базе указав ссылку на нее после флага -d
# ссылка подгрузится из переменной окружения, которую нам нужно будет указать на сервисе деплоя
# дальше мы загружаем в поключенную базу наш sql-файл с таблицами
# sudo -u postgres psql с правами суперпользователя
# psql -U user_83 -d db_83 -h 127.0.0.1 подключиться к db_83 от user_83
make install && psql -a -d $DATABASE_URL -f database.sql