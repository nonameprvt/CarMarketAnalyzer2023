import typing as tp

import csv
from pathlib import Path

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import db_properties  # contains private data so this file is not uploaded to the repository

COL_NAMES: tp.List[str] = ['id', 'item_id', 'name', 'price', 'engine', 'mileage', 'body_type', 'fuel_type',
                           'transmission', 'seller_type', 'city', 'description', 'link', 'market_type',
                           'predicted_price', 'horse_power', 'color', 'gear_box', 'steering_wheel_side',
                           'documents_ok', 'owners_counter', 'car_is_wanted', 'car_is_busted', 'brand_name',
                           'model_name', 'year', 'is_bitten']


def get_csv_from_market_state(output_path: Path, sold: bool = False, overwrite: bool = False) -> None:
    if not overwrite and output_path.exists():
        return

    table_name: str = 'selled_cars' if sold else 'current_cars_market_states'

    first_line: str = ','.join(COL_NAMES)

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
        'SELECT *'
        f'FROM {table_name};'
    )

    current_market_state = cur.fetchall()

    with open(output_path, 'w') as f:
        print(first_line, file=f)
        csv.writer(f).writerows(current_market_state)

    cur.close()
    con.close()
