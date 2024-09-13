## Пример сайта на FastAPI.

- Регистрация и авторизация пользователей.
- Подтверждение email пользователя при регистрации.
- Восстановление и изменение пароля.

Технологии:

- Базы данных. (Postgres, sqlalchemy, alembic)
- Зависимости. (Poetry)

## Начало работы.

#### Установить зависимости:

> poetry install

#### Применить миграции:

> alembic revision --autogenerate -m 'initial' \
> alembic upgrade head

#### Запустить сервер FastApi:

> uvicorn app.main:app --reload