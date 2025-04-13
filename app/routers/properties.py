"""Маршрутизация для работы со свойствами.

Содержит эндпоинты для создания и удаления свойств.
"""

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from virtualenv.run import Session

from app.database import get_db
from app.models import Property, PropertyType, PropertyValue

router = APIRouter(prefix='/properties', tags=['properties'])


@router.post('/', status_code=201)
def create_property(
        prop_in: Dict,
        db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Создает новое свойство.

    Параметры:
        prop_in (Dict): Данные свойства (uid, name, type, и values для list).
        db: Сессия БД, получаемая через Depends.
    Возвращает:
        Словарь с сообщением об успешном создании.
    Исключения:
        HTTPException 400: Если тип неверен, свойство существует или
                        отсутствуют значения для типа list.
    """
    prop_type = prop_in.get('type')
    if prop_type not in ['list', 'int']:
        raise HTTPException(
            status_code=400,
            detail='Неверный тип свойства'
        )
    if db.query(Property).filter(Property.uid == prop_in.get('uid')).first():
        raise HTTPException(
            status_code=400,
            detail='Свойство с таким uid уже существует'
        )
    if prop_type == 'list':
        if 'values' not in prop_in or not isinstance(
                prop_in['values'], list
        ) or not prop_in['values']:
            raise HTTPException(
                status_code=400,
                detail='Для свойства типа list должны быть заданы значения'
            )
        new_prop = Property(
            uid=prop_in['uid'],
            name=prop_in['name'],
            type=PropertyType.list
        )
        db.add(new_prop)
        for val in prop_in['values']:
            pv = PropertyValue(
                property_uid=prop_in['uid'],
                value_uid=val['value_uid'],
                value=val['value']
            )
            db.add(pv)
    else:
        new_prop = Property(
            uid=prop_in['uid'],
            name=prop_in['name'],
            type=PropertyType.int
        )
        db.add(new_prop)
    db.commit()
    return {'message': 'Свойство успешно создано'}


@router.delete('/{uid}')
def delete_property(uid: str, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Удаляет свойство по его uid.

    Параметры:
        uid (str): Уникальный идентификатор свойства.
        db: Сессия БД, получаемая через Depends.
    Возвращает:
        Словарь с сообщением об успешном удалении.
    Исключения:
        HTTPException 404: Если свойство не найдено.
    """
    prop = db.query(Property).filter(Property.uid == uid).first()
    if not prop:
        raise HTTPException(status_code=404, detail='Свойство не найдено')
    db.delete(prop)
    db.commit()
    return {'message': 'Свойство успешно удалено'}
