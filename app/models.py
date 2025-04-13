"""Модуль моделей SQLAlchemy для Catalog API.

Определяет структуры данных для работы со свойствами, их значениями, товарами
и связями между ними.
"""

import enum

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import (Mapped, declarative_base, mapped_column,
                            relationship)

from app.database import engine

Base = declarative_base()
Base.metadata.create_all(bind=engine)


class PropertyType(enum.Enum):
    """Перечисление типов свойств.

    Атрибуты:
        list: Свойство со списком допустимых значений.
        int: Целочисленное свойство.
    """
    list = 'list'
    int = 'int'


class Property(Base):
    """Модель свойства.

    Атрибуты:
        uid: Уникальный идентификатор свойства.
        name: Название свойства.
        type: Тип свойства (list или int).
        values: Список допустимых значений (для типа list).
    """
    __tablename__ = 'properties'
    uid: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[PropertyType] = mapped_column(
        Enum(PropertyType),
        nullable=False
    )
    values: Mapped[list['PropertyValue']] = relationship(
        'PropertyValue',
        cascade='all, delete',
        back_populates='property'
    )


class PropertyValue(Base):
    """Модель значения свойства (для свойств типа list).

    Атрибуты:
        id: Автоматически генерируемый первичный ключ.
        property_uid: Идентификатор свойства.
        value_uid: Уникальный идентификатор значения.
        value: Текстовое представление значения.
        property: Связь с моделью Property.
    """
    __tablename__ = 'property_values'
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    property_uid: Mapped[str] = mapped_column(String, ForeignKey(
        'properties.uid',
        ondelete='CASCADE'
    ), nullable=False)
    value_uid: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    property: Mapped['Property'] = relationship(
        'Property',
        back_populates='values'
    )


class Product(Base):
    """Модель товара.

    Атрибуты:
        uid: Уникальный идентификатор товара.
        name: Название товара.
        properties: Список свойств товара.
    """
    __tablename__ = 'products'
    uid: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    properties: Mapped[list['ProductProperty']] = relationship(
        'ProductProperty',
        cascade='all, delete',
        back_populates='product'
    )


class ProductProperty(Base):
    """Модель связи товара со свойством.

    Атрибуты:
        id: Автоматически генерируемый первичный ключ.
        product_uid: Идентификатор товара.
        property_uid: Идентификатор свойства.
        int_value: Значение для свойства типа int.
        value_uid: Идентификатор значения для свойства типа list.
        product: Связь с моделью Product.
        property: Связь с моделью Property.
    """
    __tablename__ = 'product_properties'
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    product_uid: Mapped[str] = mapped_column(String, ForeignKey(
        'products.uid',
        ondelete='CASCADE'
    ),
        nullable=False)
    property_uid: Mapped[str] = mapped_column(
        String,
        ForeignKey('properties.uid'),
        nullable=False
    )
    int_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    value_uid: Mapped[str | None] = mapped_column(String, nullable=True)
    product: Mapped['Product'] = relationship(
        'Product',
        back_populates='properties'
    )
    property: Mapped['Property'] = relationship('Property')
