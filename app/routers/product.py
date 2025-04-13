"""Маршруты для работы с товарами.

Содержит эндпоинты для получения, создания и удаления товаров, а также
утилиту для извлечения текстового значения свойства.
"""

from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import (Product, ProductProperty, Property, PropertyType,
                        PropertyValue)
from app.schemas import ProductCreate, ProductSchema

router = APIRouter(prefix='/product', tags=['product'])


def get_property_value(
        property_obj: Property,
        value_uid: str
) -> Optional[str]:
    """Возвращает текстовое значение свойства по value_uid.

    Параметры:
        property_obj (Property): Объект свойства с данными.
        value_uid (str): Идентификатор значения.
    Возвращает:
        Текстовое значение, если найдено, иначе None.
    """
    for pv in property_obj.values:
        if pv.value_uid == value_uid:
            return pv.value
    return None


@router.get('/{uid}', response_model=ProductSchema)
def get_product(uid: str, db: Session = Depends(get_db)) -> ProductSchema:
    """Получает товар по его uid.

    Параметры:
        uid (str): Уникальный идентификатор товара.
        db (Session): Сессия БД, получаемая через Depends.
    Возвращает:
        Данные товара в виде словаря, соответствующего ProductSchema.
    Исключения:
        HTTPException 404: Если товар не найден.
    """
    product = db.query(Product).options(
        joinedload(Product.properties).joinedload(ProductProperty.property)
    ).filter(Product.uid == uid).first()
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    prop_list = []
    for pp in product.properties:
        prop_data = {'uid': pp.property.uid, 'name': pp.property.name}
        if pp.property.type == PropertyType.list:
            prop_data['value_uid'] = pp.value_uid
            prop_data['value'] = (get_property_value(pp.property, pp.value_uid)
                                  if pp.value_uid else None)
        else:
            prop_data['value'] = pp.int_value
        prop_list.append(prop_data)
    return {'uid': product.uid, 'name': product.name, 'properties': prop_list}


@router.post('/', status_code=201)
def create_product(product_in: ProductCreate,
                   db: Session = Depends(get_db)) -> Dict[str, str]:
    """Создает новый товар.

    Параметры:
        product_in (ProductCreate): Данные товара со свойствами.
        db (Session): Сессия БД, получаемая через Depends.
    Возвращает:
        Словарь с сообщением об успешном создании товара.
    Исключения:
        HTTPException 400: Если товар существует или указано неверное
                             свойство/значение.
    """
    if db.query(Product).filter(Product.uid == product_in.uid).first():
        raise HTTPException(
            status_code=400,
            detail='Товар с таким uid уже существует'
        )
    product = Product(uid=product_in.uid, name=product_in.name)
    for prop in product_in.properties:
        db_prop = db.query(Property).filter(Property.uid == prop.uid).first()
        if not db_prop:
            raise HTTPException(
                status_code=400,
                detail=f'Свойство {prop.uid} не найдено'
            )
        if db_prop.type == PropertyType.list:
            if not prop.value_uid:
                raise HTTPException(
                    status_code=400,
                    detail=f'Для {prop.uid} необходимо указать value_uid'
                )
            valid = db.query(Property).join(Property.values).filter(
                Property.uid == prop.uid,
                PropertyValue.value_uid == prop.value_uid
            ).first()
            if not valid:
                raise HTTPException(
                    status_code=400,
                    detail=f'{prop.value_uid} для {prop.uid} недопустимо'
                )
            product_prop = ProductProperty(
                property_uid=prop.uid,
                value_uid=prop.value_uid
            )
        else:
            if prop.value is None:
                raise HTTPException(
                    status_code=400,
                    detail=f'Для {prop.uid} необходимо указать значение'
                )
            product_prop = ProductProperty(
                property_uid=prop.uid,
                int_value=prop.value
            )
        product.properties.append(product_prop)
    db.add(product)
    db.commit()
    return {'message': 'Товар успешно создан'}


@router.delete('/{uid}')
def delete_product(uid: str, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Удаляет товар по его uid.

    Параметры:
        uid (str): Уникальный идентификатор товара.
        db (Session): Сессия БД, получаемая через Depends.
    Возвращает:
        Словарь с сообщением об успешном удалении товара.
    Исключения:
        HTTPException 404: Если товар не найден.
    """
    product = db.query(Product).filter(Product.uid == uid).first()
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    db.delete(product)
    db.commit()
    return {'message': 'Товар успешно удалён'}
