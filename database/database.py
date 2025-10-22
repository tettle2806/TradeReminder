from datetime import datetime

from sqlalchemy import func, Integer, ARRAY, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, class_mapper
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from typing import Annotated, List
from sqlalchemy import String
from sqlalchemy.orm import mapped_column

from database.config import settings

DATABASE_URL = settings.get_db_url()

# Создаем асинхронный движок для работы с базой данных
engine = create_async_engine(url=DATABASE_URL)
# Создаем фабрику сессий для взаимодействия с базой данных
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

uniq_str_an = Annotated[str, mapped_column(unique=True)]  # Аннотация для уникальных строковых полей
array_or_none_an = Annotated[List[str] | None, mapped_column(ARRAY(String))]  # Аннотация для массивов строк или None
content_an = Annotated[Text, mapped_column(Text)]  # Аннотация для текстового контента, допускающего значение None


# Базовый класс для всех моделей
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  # Класс абстрактный, чтобы не создавать отдельную таблицу для него

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

    def to_dict(self) -> dict:
        """Универсальный метод для конвертации объекта SQLAlchemy в словарь"""
        # Получаем маппер для текущей модели
        columns = class_mapper(self.__class__).columns
        # Возвращаем словарь всех колонок и их значений
        return {column.key: getattr(self, column.key) for column in columns}

# Описание конфигурации
#
#     DeclarativeBase: Основной класс для всех моделей, от которого будут наследоваться все таблицы (модели таблиц). Эту особенность класса мы будем использовать неоднократно.
#
#     AsyncAttrs: Позволяет создавать асинхронные модели, что улучшает производительность при работе с асинхронными операциями.
#
#     create_async_engine: Функция, создающая асинхронный движок для соединения с базой данных по предоставленному URL.
#
#     async_sessionmaker: Фабрика сессий для асинхронного взаимодействия с базой данных. Сессии используются для выполнения запросов и транзакций.



# Декоратор для создания сессии
# Давайте сразу добавим этот декоратор в файл database.py, так как сегодня мы будем его использовать регулярно.
# Как работает этот декоратор:
#
#     connection принимает исходную функцию для обёртки.
#
#     wrapper — это функция-обёртка, которая принимает все аргументы исходной функции.
#
#     async with async_session_maker() автоматически создаёт и закрывает сессию в асинхронном режиме, освобождая вас от необходимости управлять сессией вручную.
#
#     Сессия передаётся в исходную функцию через аргумент session.
#
#     В случае ошибки выполняется откат транзакции через rollback(), а затем сессия закрывается.


def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                # Явно не открываем транзакции, так как они уже есть в контексте
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()  # Откатываем сессию при ошибке
                raise e  # Поднимаем исключение дальше
            finally:
                await session.close()  # Закрываем сессию

    return wrapper