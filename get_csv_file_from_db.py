import csv
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import db_properties


def get_csv_from_market_state():
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
        'FROM current_cars_market_states;'
    )

    current_market_state = cur.fetchall()

    c = csv.writer(open("current_market_state.csv","w"))
    c.writerows(current_market_state)

    cur.close()
    con.close()

get_csv_from_market_state()
