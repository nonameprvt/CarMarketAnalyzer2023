from flask import Flask, jsonify, request
from flask_cors import CORS
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import db_properties

app = Flask(__name__)
CORS(app)


def sql_ops(sql_text):
    con = connect(
        user=db_properties.LOGIN,
        database=db_properties.DATABASE,
        host=db_properties.IP,
        password=db_properties.PASSWORD,
        port=db_properties.PORT
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute(sql_text)
    result = cur.fetchall()
    cur.close()
    con.close()
    return result


def build_statement_prefix(current_statement):
    if current_statement == '':
        return 'WHERE'
    else:
        return ' AND'


def check_query_param_exist(param):
    return param is not None and param not in ['null', 'undefined', 'NaN', '']


def check_param_is_digit(param):
    return param.isdigit()


def build_where_statement(
        brand=None,
        model=None,
        min_year=None,
        max_year=None,
        fuel_type=None,
        body_type=None,
        show_bitten_cars=None,
        min_price=None,
        max_price=None,
        min_horse_power=None,
        max_horse_power=None,
        min_mileage=None,
        max_mileage=None
):
    where_statement = ''
    if check_query_param_exist(min_year):
        where_statement += build_statement_prefix(where_statement) + ' year >= ' + min_year
    if check_query_param_exist(max_year):
        where_statement += build_statement_prefix(where_statement) + ' year <= ' + max_year
    if check_query_param_exist(brand):
        where_statement += build_statement_prefix(where_statement) + ' brand_name = \'' + brand + '\''
    if check_query_param_exist(model):
        where_statement += build_statement_prefix(where_statement) + ' model_name = \'' + model + '\''
    if check_query_param_exist(fuel_type):
        where_statement += build_statement_prefix(where_statement) + ' fuel_type = \'' + fuel_type + '\''
    if check_query_param_exist(body_type):
        where_statement += build_statement_prefix(where_statement) + ' body_type = \'' + body_type + '\''
    if check_query_param_exist(show_bitten_cars):
        where_statement += build_statement_prefix(where_statement) + ' NOT is_bitten'
    if check_query_param_exist(min_price) and check_param_is_digit(min_price):
        where_statement += build_statement_prefix(where_statement) + ' price >= ' + min_price
    if check_query_param_exist(max_price) and check_param_is_digit(max_price):
        where_statement += build_statement_prefix(where_statement) + ' price <= ' + max_price
    if check_query_param_exist(min_horse_power):
        where_statement += build_statement_prefix(where_statement) + ' horse_power >= ' + min_horse_power
    if check_query_param_exist(max_horse_power):
        where_statement += build_statement_prefix(where_statement) + ' horse_power <= ' + max_horse_power
    if check_query_param_exist(min_mileage):
        where_statement += build_statement_prefix(where_statement) + ' mileage >= ' + min_mileage
    if check_query_param_exist(max_mileage):
        where_statement += build_statement_prefix(where_statement) + ' mileage <= ' + max_mileage

    return where_statement


@app.route('/brand/list')
def brand_list():
    sql_text = 'SELECT DISTINCT(brand_name) FROM current_cars_market_states ORDER BY brand_name;'
    car_list = []

    for car in sql_ops(sql_text):
        car_list.append({'id': car, 'name': car})

    return jsonify(car_list[1:])

@app.route('/model/list')
def model_list():
    brand = request.args.get('brand')
    sql_text = (
        'SELECT DISTINCT(model_name) FROM current_cars_market_states '
        'WHERE brand_name = \'' + brand + '\' ORDER BY model_name;'
    )
    car_list = []

    for car in sql_ops(sql_text):
        car_list.append({'id': car, 'name': car})

    return jsonify(car_list[1:])


@app.route('/fuel-type/list')
def fuel_type_list():
    sql_text = 'SELECT DISTINCT(fuel_type) FROM current_cars_market_states ORDER BY fuel_type;'
    car_list = []

    for car in sql_ops(sql_text):
        if 'Ошибка' in car:
            continue
        car_list.append(car)

    return jsonify(car_list)


@app.route('/body-type/list')
def body_type_list():
    sql_text = 'SELECT DISTINCT(body_type) FROM current_cars_market_states ORDER BY body_type;'
    car_list = []

    for car in sql_ops(sql_text):
        if 'Ошибка' in car:
            continue
        car_list.append(car)

    return jsonify(car_list)


@app.route('/cars/search')
def cars_search():
    cursor = request.args.get('cursor')
    if not check_query_param_exist(cursor):
        cursor = 0
    where_statement = build_where_statement(
        request.args.get('brand'),
        request.args.get('model'),
        request.args.get('min_year'),
        request.args.get('max_year'),
        request.args.get('fuel_type'),
        request.args.get('body_type'),
        request.args.get('show_bitten_cars'),
        request.args.get('min_price'),
        request.args.get('max_price'),
        request.args.get('min_horse_power'),
        request.args.get('max_horse_power'),
        request.args.get('min_mileage'),
        request.args.get('max_mileage')
    )
    sz = int(cursor) * 10 + 11
    sql_text = (
        'SELECT item_id, brand_name, model_name, year, body_type, '
        'fuel_type, mileage, engine, transmission, horse_power, is_bitten, '
        'price, market_type, link FROM current_cars_market_states ' + 
        where_statement + ' ORDER BY item_id LIMIT ' + str(sz) + ';'
    )

    tmp = sql_ops(sql_text)

    has_next_page = len(tmp) == sz
    response = {'results': [], 'has_next_page': has_next_page}
    car_list = []

    for i in range(max(int(cursor) * 10, 0), len(tmp)):
        car_list.append({
            'id': tmp[i][0],
            'brand': tmp[i][1],
            'model': tmp[i][2],
            'year': tmp[i][3],
            'body_type':tmp[i][4],
            'fuel_type':tmp[i][5],
            'mileage':tmp[i][6],
            'engine':tmp[i][7],
            'transmission':tmp[i][8],
            'horse_power':tmp[i][9],
            'is_bitten': 'Да' if tmp[i][10] else 'Нет',
            'price': tmp[i][11],
            'market_type':tmp[i][12],
            'link': tmp[i][13]
        })

    response['results'] = car_list
    return response


if __name__ == '__main__':
    app.run()
