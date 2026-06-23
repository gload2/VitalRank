-- Настройка на уровне БД. Таблицы создаёт SQLAlchemy (create_all) при старте бэка.
-- База vitalrank создаётся автоматически через переменные POSTGRES_* в docker-compose.
-- Файл оставлен под будущие расширения и настройки, если понадобятся.

ALTER DATABASE vitalrank SET client_encoding TO 'UTF8';
