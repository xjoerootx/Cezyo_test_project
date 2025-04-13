"""Модуль загрузки тестовых данных в базу.

Загружает данные из файла vacancy.json и вставляет их в БД, если база
данных пуста.
"""

import json
import os

from app.database import SessionLocal
from app.models import (Product, ProductProperty, Property, PropertyType,
                        PropertyValue)


def load_seed_data() -> None:
    """Загружает тестовые данные из vacancy.json в базу данных.

    Если в БД уже присутствуют товары, загрузка не производится.
    Если файл данных не найден, выводится сообщение об ошибке.
    Сообщает об успехе или возникновении ошибки при загрузке.
    """
    session = SessionLocal()
    try:
        if session.query(Product).first():
            print('Тестовые данные уже загружены в БД, загрузка остановлена.')
            return

        file_path = os.path.join(os.path.dirname(__file__), 'vacancy.json')
        if not os.path.exists(file_path):
            print(
                f'Не найден{file_path} , загрузка остановлена.'
            )
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for prop in data.get('properties', []):
            new_prop = Property(
                uid=prop['uid'],
                name=prop['name'],
                type=PropertyType(prop['type'])
            )
            session.add(new_prop)
            if new_prop.type == PropertyType.list and 'values' in prop:
                for val in prop['values']:
                    value_id = val.get('uid') or val.get('value_uid')
                    new_val = PropertyValue(
                        property_uid=new_prop.uid,
                        value_uid=value_id,
                        value=val['value']
                    )
                    session.add(new_val)
        session.commit()

        for prod in data.get('products', []):
            new_product = Product(uid=prod['uid'], name=prod['name'])
            for prod_prop in prod.get('properties', []):
                # Проверяем, существует ли указанное свойство
                db_prop = session.query(Property).filter(
                    Property.uid == prod_prop['uid']
                ).first()
                if not db_prop:
                    print(
                        f"Свойство {prod_prop['uid']} не найдено для товара\
                        {prod['uid']}, пропускаем это свойство."
                    )
                    continue
                if db_prop.type == PropertyType.list:
                    product_prop = ProductProperty(
                        property_uid=prod_prop['uid'],
                        value_uid=prod_prop['value_uid']
                    )
                else:
                    product_prop = ProductProperty(
                        property_uid=prod_prop['uid'],
                        int_value=prod_prop['value']
                    )
                new_product.properties.append(product_prop)
            session.add(new_product)
        session.commit()

        print('Тестовые данные успешно загружены в БД.')

    except Exception as e:
        session.rollback()
        print('Ошибка при загрузке тестовых данных:', e)
    finally:
        session.close()
