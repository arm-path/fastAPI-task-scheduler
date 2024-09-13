## Пример сайта на FastAPI.

- Регистрация и авторизация пользователей.
- Подтверждение email пользователя при регистрации.
- Восстановление и изменение пароля.
- CRUD категории, планировщиков, задач и подзадач.

Технологии:

- Базы данных. (Postgres, sqlalchemy, alembic)
- Зависимости. (Poetry)
- Пагинация. (FastApi-pagination[sqlalchemy])

## Начало работы.

#### Установить зависимости:

> poetry install

#### Применить миграции:

> alembic revision --autogenerate -m 'initial' \
> alembic upgrade head

#### Запустить сервер FastApi:

> uvicorn app.main:app --reload