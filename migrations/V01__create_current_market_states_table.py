from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import db_properties

con = connect(
    user=db_properties.LOGIN,
    database=db_properties.DATABASE,
    host=db_properties.IP,
    password=db_properties.PASSWORD,
    port=db_properties.PORT
)
con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = con.cursor()

cur.execute(
    'CREATE TABLE IF NOT EXISTS current_cars_market_states ('
    'id SERIAL PRIMARY KEY NOT NULL,'
    'item_id TEXT NOT NULL,'
    'name TEXT NOT NULL,'
    'price TEXT,'
    'engine TEXT,'
    'mileage TEXT,'
    'body_type TEXT,'
    'fuel_type TEXT,'
    'transmission TEXT,'
    'seller_type TEXT,'
    'city TEXT,'
    'description TEXT,'
    'link TEXT,'
    'market_type TEXT NOT NULL,'
    'predicted_price TEXT'
    ');'
)

cur.execute(
    'CREATE UNIQUE INDEX IF NOT EXISTS current_cars_market_states_index_ '
    'ON current_cars_market_states(item_id, market_type);'
)

cur.execute(
    'CREATE TABLE IF NOT EXISTS selled_cars ('
    'id SERIAL PRIMARY KEY NOT NULL,'
    'item_id TEXT NOT NULL,'
    'name TEXT NOT NULL,'
    'price TEXT,'
    'engine TEXT,'
    'mileage TEXT,'
    'body_type TEXT,'
    'fuel_type TEXT,'
    'transmission TEXT,'
    'seller_type TEXT,'
    'city TEXT,'
    'description TEXT,'
    'link TEXT,'
    'market_type TEXT NOT NULL,'
    'predicted_price TEXT'
    ');'
)

cur.execute(
    'CREATE UNIQUE INDEX IF NOT EXISTS selled_cars_index_ '
    'ON selled_cars(item_id, market_type);'
)

cur.close()
con.close()
