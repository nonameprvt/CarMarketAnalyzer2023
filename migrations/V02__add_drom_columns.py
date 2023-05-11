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
    """
    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS horse_power INTEGER;

    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS color TEXT;

    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS gear_box TEXT;

    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS steering_wheel_side TEXT;

    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS documents_ok TEXT;

    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS owners_counter TEXT;

    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS car_is_wanted TEXT;

    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS car_is_busted TEXT;

    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS brand_name TEXT;

    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS model_name TEXT;

    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS year INTEGER;

    ALTER TABLE current_cars_market_states
    ADD COLUMN IF NOT EXISTS is_bitten BOOLEAN DEFAULT FALSE;
    """
)

cur.execute(
    """
    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS horse_power INTEGER;

    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS color TEXT;

    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS gear_box TEXT;

    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS steering_wheel_side TEXT;

    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS documents_ok TEXT;

    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS owners_counter TEXT;

    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS car_is_wanted TEXT;

    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS car_is_busted TEXT;

    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS brand_name TEXT;

    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS model_name TEXT;

    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS year INTEGER;

    ALTER TABLE selled_cars
    ADD COLUMN IF NOT EXISTS is_bitten BOOLEAN DEFAULT FALSE;
    """
)

cur.close()
con.close()
