## Пример сайта на FastAPI.

- Регистрация и авторизация пользователей.
- Подтверждение email пользователя при регистрации.
- Восстановление и изменение пароля.
- CRUD категории, планировщиков, задач и подзадач.
- CRUD категории, планировщиков и задач.
- Получение задач по датам.
- Отчеты по выполненным задачам.

Технологии:

- Базы данных. (Postgres, sqlalchemy, alembic)
- Зависимости. (Poetry)
- Пагинация. (FastApi-pagination[sqlalchemy])

## Начало работы (Dev).

#### Установить зависимости:

> poetry install

#### Применить миграции:

> alembic revision --autogenerate -m 'initial' \
> alembic upgrade head

#### Запустить сервер FastApi:

> uvicorn app.main:app --reload


## Начало работы (Prod).

> Docker-compose up --build