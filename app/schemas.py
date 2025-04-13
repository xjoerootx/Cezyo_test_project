"""Схемы Pydantic для Catalog API.

Определяет структуры данных для передачи и валидации информации о
свойствах, товарах и их связях.
"""

from typing import List, Literal, Optional, Union

from pydantic import BaseModel


class PropertyValueSchema(BaseModel):
    """Схема для значения свойства.

    Атрибуты:
        value_uid: Уникальный идентификатор значения.
        value: Текстовое представление значения.
    """
    value_uid: str
    value: str

    class Config:
        """Конфигурация схемы PropertyValueSchema."""
        from_attributes = True


class PropertySchema(BaseModel):
    """Схема для свойства.

    Атрибуты:
        uid: Уникальный идентификатор.
        name: Название свойства.
        type: Тип свойства (list или int).
        values: Список допустимых значений (опционально).
    """
    uid: str
    name: str
    type: str
    values: Optional[List[PropertyValueSchema]] = None

    class Config:
        """Конфигурация схемы PropertySchema."""
        from_attributes = True


class ProductPropertyOut(BaseModel):
    """Схема свойства товара (вывод).

    Атрибуты:
        uid: Идентификатор свойства.
        name: Название свойства.
        value_uid: Идентификатор выбранного значения (для list).
        value: Фактическое значение (число или текст).
    """
    uid: str
    name: str
    value_uid: Optional[str] = None
    value: Optional[Union[int, str]] = None


class ProductSchema(BaseModel):
    """Схема товара.

    Атрибуты:
        uid: Уникальный идентификатор товара.
        name: Название товара.
        properties: Список свойств товара.
    """
    uid: str
    name: str
    properties: List[ProductPropertyOut]

    class Config:
        """Конфигурация схемы ProductSchema."""
        from_attributes = True


class ProductPropertyCreate(BaseModel):
    """Схема создания связи товара со свойством.

    Атрибуты:
        uid: Идентификатор свойства.
        value_uid: Идентификатор выбранного значения (для list).
        value: Числовое значение (для int).
    """
    uid: str
    value_uid: Optional[str] = None
    value: Optional[int] = None


class ProductCreate(BaseModel):
    """Схема создания товара.

    Атрибуты:
        uid: Уникальный идентификатор товара.
        name: Название товара.
        properties: Список свойств, привязанных к товару.
    """
    uid: str
    name: str
    properties: List[ProductPropertyCreate]


class PropertyCreateList(BaseModel):
    """Схема создания свойства типа list.

    Атрибуты:
        uid: Уникальный идентификатор.
        name: Название свойства.
        type: Фиксированное значение "list".
        values: Список допустимых значений.
    """
    uid: str
    name: str
    type: Literal['list'] = 'list'
    values: List[PropertyValueSchema]


class PropertyCreateInt(BaseModel):
    """Схема создания свойства типа int.

    Атрибуты:
        uid: Уникальный идентификатор.
        name: Название свойства.
        type: Фиксированное значение "int".
    """
    uid: str
    name: str
    type: Literal['int'] = 'int'


PropertyCreate = Union[PropertyCreateList, PropertyCreateInt]
