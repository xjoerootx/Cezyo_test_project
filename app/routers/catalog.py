"""Маршруты для работы с каталогом товаров.

Содержит эндпоинты для получения каталога с пагинацией и фильтрацией, а также
утилиту для получения текстового значения свойства.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session, aliased, joinedload

from app.database import get_db
from app.models import Product, ProductProperty, Property, PropertyType

router = APIRouter(prefix='/catalog', tags=['catalog'])


def get_property_value(
        property_obj: Property,
        value_uid: str
) -> Optional[str]:
    """Возвращает текстовое значение свойства по value_uid.

    Параметры:
        property_obj (Property): Объект свойства с допустимыми значениями.
        value_uid (str): Идентификатор значения.
        Возвращает:
        Текстовое представление значения или None.
    """
    for pv in property_obj.values:
        if pv.value_uid == value_uid:
            return pv.value
    return None


@router.get('/', response_model=Dict[str, Any])
def get_catalog(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    name: Optional[str] = Query(None),
    sort: str = Query('uid', regex='^(uid|name)$'),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Получает список товаров (каталог) с пагинацией и фильтрами.

    Параметры запроса:
        page (int): Номер страницы.
        page_size (int): Количество товаров на странице.
        name (str, optional): Фильтр по имени товара.
        sort (str): Сортировка ("uid" или "name").
        Дополнительные параметры с префиксом "property_" для фильтрации.
        Возвращает:
        Словарь с ключами "products" (список товаров) и "count" (общее число).
    """
    query = db.query(Product)
    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))
    filters: Dict[str, Dict[str, Any]] = {}
    for key, value in request.query_params.items():
        if key.startswith('property_'):
            parts = key.split('_')
            if parts[-1] in ['from', 'to']:
                prop_uid = '_'.join(parts[1:-1])
                if prop_uid not in filters:
                    filters[prop_uid] = {
                        'from': None,
                        'to': None,
                        'values': []
                    }
                filters[prop_uid][parts[-1]] = value
            else:
                prop_uid = '_'.join(parts[1:])
                if prop_uid not in filters:
                    filters[prop_uid] = {
                        'from': None,
                        'to': None,
                        'values': []
                    }
                filters[prop_uid]['values'].append(value)
    for prop_uid, condition in filters.items():
        pp_alias = aliased(ProductProperty)
        query = query.join(
            pp_alias,
            Product.uid == pp_alias.product_uid
        ).filter(pp_alias.property_uid == prop_uid)
        if condition['values']:
            query = query.filter(pp_alias.value_uid.in_(condition['values']))
        else:
            if condition['from']:
                query = query.filter(
                    pp_alias.int_value >= int(condition['from'])
                )
            if condition['to']:
                query = query.filter(
                    pp_alias.int_value <= int(condition['to'])
                )
    if sort == 'name':
        query = query.order_by(Product.name)
    else:
        query = query.order_by(Product.uid)
    total_count = query.distinct().count()
    products = query.options(
        joinedload(Product.properties).joinedload(ProductProperty.property)
    ).offset((page - 1) * page_size).limit(page_size).all()
    result_products = []
    for prod in products:
        prop_list = []
        for pp in prod.properties:
            prop_data = {'uid': pp.property.uid, 'name': pp.property.name}
            if pp.property.type == PropertyType.list:
                prop_data['value_uid'] = pp.value_uid
                prop_data['value'] = get_property_value(
                    pp.property, pp.value_uid
                ) if pp.value_uid else None
            else:
                prop_data['value'] = pp.int_value
            prop_list.append(prop_data)
        result_products.append({
            'uid': prod.uid,
            'name': prod.name,
            'properties': prop_list
        })
    return {'products': result_products, 'count': total_count}


@router.get('/filter/', response_model=Dict[str, Any])
def catalog_filter(
    request: Request,
    name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Получает статистику по фильтрам каталога товаров.

    Параметры запроса:
        name (str, optional): Фильтр по имени товара.
        Дополнительные параметры с префиксом "property_".
        Возвращает:
        Словарь с числом товаров и статистикой для каждого свойства.
    """
    query = db.query(Product)
    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))
    filters: Dict[str, Dict[str, Any]] = {}
    for key, value in request.query_params.items():
        if key.startswith('property_'):
            parts = key.split('_')
            if parts[-1] in ['from', 'to']:
                prop_uid = '_'.join(parts[1:-1])
                if prop_uid not in filters:
                    filters[prop_uid] = {
                        'from': None,
                        'to': None,
                        'values': []
                    }
                filters[prop_uid][parts[-1]] = value
            else:
                prop_uid = '_'.join(parts[1:])
                if prop_uid not in filters:
                    filters[prop_uid] = {
                        'from': None,
                        'to': None,
                        'values': []
                    }
                filters[prop_uid]['values'].append(value)
    for prop_uid, condition in filters.items():
        pp_alias = aliased(ProductProperty)
        query = query.join(
            pp_alias,
            Product.uid == pp_alias.product_uid
        ).filter(pp_alias.property_uid == prop_uid)
        if condition['values']:
            query = query.filter(pp_alias.value_uid.in_(condition['values']))
        else:
            if condition['from']:
                query = query.filter(
                    pp_alias.int_value >= int(condition['from'])
                )
            if condition['to']:
                query = query.filter(
                    pp_alias.int_value <= int(condition['to'])
                )
    filtered_products = query.distinct().all()
    product_ids = [p.uid for p in filtered_products]
    result = {'count': len(filtered_products)}
    properties = db.query(Property).all()
    for prop in properties:
        q = db.query(ProductProperty).filter(
            ProductProperty.product_uid.in_(product_ids),
            ProductProperty.property_uid == prop.uid
        )
        if prop.type == PropertyType.list:
            groups = {}
            for pp in q.all():
                groups[pp.value_uid] = groups.get(pp.value_uid, 0) + 1
            result[prop.uid] = groups
        else:
            values = [
                pp.int_value for pp in q.all() if pp.int_value is not None
            ]
            if values:
                result[prop.uid] = {
                    'min_value': min(values),
                    'max_value': max(values)
                }
            else:
                result[prop.uid] = {'min_value': None, 'max_value': None}
    return result
