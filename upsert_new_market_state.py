from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import db_properties


def get_car_ids(parsed_data):
    car_ids = []
    for data in parsed_data:
        car_ids.append(data['item_id'])
    return car_ids


def move_selled_cars(data, market_type):
    con = connect(
        user=db_properties.LOGIN,
        database=db_properties.DATABASE,
        host=db_properties.IP,
        password=db_properties.PASSWORD,
        port=db_properties.PORT
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    car_ids = get_car_ids(data)

    cur.execute(
        'SELECT '
        'item_id, name, price, engine, '
        'mileage, body_type, fuel_type, '
        'transmission, seller_type, city, description, '
        'link, market_type, predicted_price '
        'FROM current_cars_market_states '
        'WHERE market_type = %s AND item_id NOT IN %s',
        (market_type, tuple(car_ids))
    )

    selled_cars = cur.fetchall()

    if not selled_cars:
        return

    cur.execute(
        'DELETE FROM current_cars_market_states '
        'WHERE market_type = %s AND item_id NOT IN %s',
        (market_type, tuple(car_ids))
    )

    args = ','.join(cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", i).decode('utf-8')
                for i in selled_cars)

    cur.execute(
        'INSERT INTO selled_cars('
        'item_id, name, price, engine, '
        'mileage, body_type, fuel_type, '
        'transmission, seller_type, city, description, '
        'link, market_type, predicted_price) '
        'VALUES ' + (args)
    )

    cur.close()
    con.close()


def upsert_new_data(data):
    con = connect(
        user=db_properties.LOGIN,
        database=db_properties.DATABASE,
        host=db_properties.IP,
        password=db_properties.PASSWORD,
        port=db_properties.PORT
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    args = ','.join(cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", tuple(i.values())).decode('utf-8')
                for i in data)

    cur.execute(
        'INSERT INTO current_cars_market_states('
        'item_id, name, price, engine,'
        'mileage, body_type, fuel_type,'
        'transmission, seller_type, city, description,'
        'link, market_type) '
        'VALUES ' + (args) +
        'ON CONFLICT (item_id, market_type) DO UPDATE SET '
        'name = EXCLUDED.name,'
        'price = EXCLUDED.price,'
        'engine = EXCLUDED.engine,'
        'mileage = EXCLUDED.mileage,'
        'body_type = EXCLUDED.body_type,'
        'fuel_type = EXCLUDED.fuel_type,'
        'transmission = EXCLUDED.transmission,'
        'seller_type = EXCLUDED.seller_type,'
        'city = EXCLUDED.city,'
        'description = EXCLUDED.description;'
    )

    cur.close()
    con.close()


example_data = [
    {
        'item_id': '111',
        'name': 'Nissan1',
        'price': '1000000',
        'engine': 'full',
        'mileage': '10000',
        'body_type': 'body',
        'fuel_type': 'fuel',
        'transmission': 'transmission',
        'seller_type': 'seller',
        'city': 'Moscow',
        'description': 'Please get my car',
        'link': 'avito.ru/111',
        'market_type': 'avito',
    },
    {
        'item_id': '222',
        'name': 'Nissan2',
        'price': '1000000',
        'engine': 'full',
        'mileage': '10000',
        'body_type': 'body',
        'fuel_type': 'fuel',
        'transmission': 'transmission',
        'seller_type': 'seller',
        'city': 'Moscow',
        'description': 'Please get my car',
        'link': 'avito.ru/111',
        'market_type': 'avito',
    },
    {
        'item_id': '333',
        'name': 'Nissan',
        'price': '2000000',
        'engine': 'full1',
        'mileage': '20000',
        'body_type': 'body1',
        'fuel_type': 'fuel1',
        'transmission': 'transmission',
        'seller_type': 'seller',
        'city': 'Moscow',
        'description': 'Please get my car pleeeeease',
        'link': 'avito.ru/111',
        'market_type': 'avito',
    },
    {
        'item_id': '444',
        'name': 'Nissan',
        'price': '1000001',
        'engine': 'full',
        'mileage': '10000',
        'body_type': 'body',
        'fuel_type': 'fuel',
        'transmission': 'transmission',
        'seller_type': 'seller',
        'city': 'Moscow',
        'description': 'Please get my car',
        'link': 'avito.ru/111/selling',
        'market_type': 'avito',
    },
    {
        'item_id': '555',
        'name': 'Nissan',
        'price': '1000000',
        'engine': 'full',
        'mileage': '10000',
        'body_type': 'body',
        'fuel_type': 'fuel',
        'transmission': 'transmission',
        'seller_type': 'seller',
        'city': 'Moscow',
        'description': 'Please get my car',
        'link': 'avito.ru/111',
        'market_type': 'avito',
    },
    {
        'item_id': '111',
        'name': 'Nissan',
        'price': '1000000',
        'engine': 'full',
        'mileage': '10000',
        'body_type': 'body',
        'fuel_type': 'fuel',
        'transmission': 'transmission',
        'seller_type': 'seller',
        'city': 'Moscow',
        'description': 'Please get my car',
        'link': 'avito.ru/111',
        'market_type': 'autoru',
    }
]
