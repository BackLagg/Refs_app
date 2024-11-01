# Referral System Application

Это проект реферальной системы, построенный на FastAPI и PostgreSQL. Приложение поддерживает создание и управление реферальными кодами и регистрацию пользователей через реферальную программу.

## Оглавление

- [Стек технологий](#стек-технологий)
- [Установка и запуск проекта](#установка-и-запуск-проекта)
  - [1. Клонирование репозитория](#1-клонирование-репозитория)
  - [2. Первый(простой) путь запуска через Docker](#2-первыйпростой-путь-запуска-через-docker)
  - [3. Второй путь запуска приложения](#3-второй-путь-запуска-приложения)
  - [4. Запуск тестов](#4-запуск-тестов)

## Стек технологий

- **Backend**: FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, FastApi-Users
- **Frontend**: В разработке
- **Docker**: для контейнеризации и удобной разработки

## Установка и запуск проекта

### 1. Клонирование репозитория

Склонируйте репозиторий на своё устройство:

    git clone <https://github.com/BackLagg/Refs_app>
    cd <имя проекта>

### 2. Первый(простой) путь запуска через Docker

#### a. Установите Docker Desktop, если у вас windows, или сам Docker, если Linux

#### b. Менять ничего не нужно, просто соберите и запустите.
    
    docker-compose build
    docker-compose up

Приложенине запуститься на адресе http://localhost:8080

Можете работать с приложением


### ВАЖНО: 
#### а. Из-за недостаточности ресурсов или иных проблемах, БД может перезапуститься тем самым нарушив поряток создания контейнеров и нарушив миграции. Пересоберите ещё раз контейнер.
#### b. Из проблемы выше также может случиться, что контейнер с основным приложением, может не получить доступ к БД и упасть, просто ещё раз его запустите, или перезапустите сам кластер.


### 3. Второй путь запуска приложения

#### а. Установите Postgres, Redis 
#### b. Отредактируйте .env файл с учёётом ваших данных

### База данных
DB_HOST=<ваш_хост> //по стандарту localhost
DB_PORT=<ваш_порт>
DB_NAME=<имя_базы>
DB_USER=<пользователь>
DB_PASS=<пароль>
SECRET_KEY=<секретный_ключ>

REDIS_HOST=<ваш_хост> //по стандарту localhost
REDIS_PORT=<ваш_порт>


#### c. Установите зависимости
    pip install -r requirements.txt

#### d. Запустите приложение
    uvicorn src.app:app --reload --port 8080

Можете пользоваться

## 4. Запуск тестов

Перейдите в директориюпроектов и запустите pytest

    pytest --asyncio-mode=auto

Приложение асинхронное поэтому тесты тоже асинхронные важно устанавливать флаг --asyncio-mode=auto