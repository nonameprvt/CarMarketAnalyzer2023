import csv
import json
import time

import upsert_new_market_state


def json_to_csv(json_array, file_name):
    with open(file_name, 'w', newline='') as output_file:
        csv_writer = csv.writer(output_file)

        csv_writer.writerow(json_array[0].keys())

        for item in json_array:
            csv_writer.writerow(item.values())

    with open(file_name, 'r') as output_file:
        return output_file.read()


def upsert_after_parser(parsed_data, brand_name, model_name=None):
    if len(parsed_data) == 0:
        return
    data = []
    for item in parsed_data:
        data.append(json.loads(item))
    print(len(data))
    if len(data) == 0:
        return
    time.sleep(2)
    upsert_new_market_state.upsert_new_data(data)
    time.sleep(2)
    upsert_new_market_state.move_selled_cars(data, 'avito', brand_name, model_name)
    time.sleep(2)
    upsert_new_market_state.move_fake_selled_cars_back(data, 'avito', brand_name, model_name)