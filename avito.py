import upsert_new_market_state
import json
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from price_prediction import predict


class CaptchaException(Exception):
    pass

def parse_item_id_by_link(link):
    link_arr = link.split(sep='_')
    return link_arr[-1]

def parse_engine_and_horse_power(engine_elem):
    if '(' not in engine_elem:
        return engine_elem, 0
    engine_elem = engine_elem.split('(')
    if engine_elem[0][-1] == ' ':
        return engine_elem[0][:len(engine_elem[0]) - 1], int(engine_elem[1].split(' ')[0])
    return engine_elem[0], int(engine_elem[1].split(' ')[0])

def check_if_first_elem_is_digit(first_elem):
    splitted_elem = first_elem.split(' ')
    maybe_digit_value = ''
    for idx in range(len(splitted_elem) - 1):
        maybe_digit_value += splitted_elem[idx]
    if maybe_digit_value.isdigit():
        return int(maybe_digit_value)
    return 0


def get_by_pages(browser, brand_name):
    car_ids = []
    data = set()
    model_name = 'Ошибка'
    page_idx = 0
    while True:
        if page_idx > 100:
            raise CaptchaException(brand_name + ';' + model_name)
        page_idx += 1
        time1 = time.time()
        # Проверяем, есть ли автомобили на этой странице.
        no_results_title = browser.find_elements(
            By.XPATH, "//h2[contains(@class, 'no-results-title')]")
        if len(no_results_title) > 0:
            break

        time.sleep(2.5)

        name = browser.find_elements(
            By.XPATH, "//h3[contains(@itemprop, 'name')]")
        # достаем -> .text

        price = browser.find_elements(
            By.XPATH, "//meta[contains(@itemprop, 'price')]")
        # достаем четные элементы, там цена. В нечетных RUB

        params = browser.find_elements(
            By.XPATH,
            "//p[contains(@data-marker, 'item-specific-params')]")
        # достаем -> .text.split(', '), получаем массив характеристик

        description = browser.find_elements(
            By.CLASS_NAME, "iva-item-descriptionStep-C0ty1")
        # достаем -> .text

        seller = browser.find_elements(
            By.XPATH, "//div[contains(@data-marker, 'item-line')]")
        # достаем -> .text

        city = browser.find_elements(
            By.XPATH, "//div[contains(@class, 'geo-root')]")
        # достаем -> .text

        link = browser.find_elements(
            By.XPATH, "//a[contains(@data-marker, 'item-title')]")
        # достаем -> .get_attribute('href')

        time.sleep(1.5)
        cnt = 0

        for car in range(len(name)):
            if len(city) > car and city[car].text != 'Москва':
                continue

            if len(link) <= car:
                continue
                
            car_json = {
                'item_id': 'Ошибка',
                'name': 'Ошибка',
                'price': 0,
                'engine': 'Ошибка',
                'mileage': 0,
                'body_type': 'Ошибка',
                'fuel_type': 'Ошибка',
                'transmission': 'Ошибка',
                'seller_type': 'Ошибка',
                'city': 'Ошибка',
                'description': 'Ошибка',
                'link': 'Ошибка',
                'market_type': 'avito',
                'predicted_price': 0,
                'horse_power': 0,
                'color': 'Ошибка',
                'gear_box': 'Ошибка',
                'steering_wheel_side': 'Ошибка',
                'documents_ok': 'Ошибка',
                'owners_counter': 'Ошибка',
                'car_is_wanted': 'Ошибка',
                'car_is_busted': 'Ошибка',
                'brand_name': brand_name,
                'model_name': 'Ошибка',
                'year': 0,
                'is_bitten': False,
            }

            car_json['link'] = link[car].get_attribute('href')
            car_json['item_id'] = parse_item_id_by_link(
                car_json['link'])

            if car_json['item_id'] in car_ids:
                continue
            else:
                car_ids.append(car_json['item_id'])

            specs = params[car].text.split(', ')
            i = 0
            if specs[0] == 'Битый':
                i = 1
                car_json['is_bitten'] = True
            if len(specs) > i + 4:
                mileage_tmp = check_if_first_elem_is_digit(specs[i])
                if mileage_tmp != 0:
                    car_json['mileage'] = mileage_tmp
                car_json['engine'], car_json['horse_power'] = parse_engine_and_horse_power(specs[i + 1])
                car_json['body_type'] = specs[i + 2]
                car_json['transmission'] = specs[i + 3]
                car_json['fuel_type'] = specs[i + 4]
            elif len(specs) == i + 4:
                mileage_tmp = check_if_first_elem_is_digit(specs[i])
                if mileage_tmp != 0:
                    car_json['mileage'] = mileage_tmp
                    car_json['engine'], car_json['horse_power'] = parse_engine_and_horse_power(specs[i + 1])
                    car_json['transmission'] = specs[i + 2]
                    car_json['fuel_type'] = specs[i + 3]
                else:
                    car_json['engine'], car_json['horse_power'] = parse_engine_and_horse_power(specs[i])
                    car_json['body_type'] = specs[i + 1]
                    car_json['transmission'] = specs[i + 2]
                    car_json['fuel_type'] = specs[i + 3]

            if len(name) > car:
                car_json['name'] = name[car].text
                if car_json['name'] == '' or car_json['name'] == 'Ошибка':
                    print('Bad car name')
                    continue
                brand_name_size = len(brand_name.split(' '))
                splitted_name = car_json['name'].split(', ')
                car_json['year'] = int(splitted_name[1])
                splitted_brand_model = splitted_name[0].split(' ')
                parsed_model_name = ''
                for idx in range(brand_name_size, len(splitted_brand_model)):
                    if idx > brand_name_size:
                        parsed_model_name += ' '
                    parsed_model_name += splitted_brand_model[idx]
                car_json['model_name'] = parsed_model_name
                model_name = parsed_model_name
            else:
                print(str(len(name)) + ' > ' + str(car))

            if len(price) > 2 * car + 1:
                car_json['price'] = int(price[2 * car + 1].get_attribute('content'))
                car_json['predicted_price'] = car_json['price']

            if len(seller) > car:
                car_json['seller_type'] = seller[car].text

            if len(city) > car:
                car_json['city'] = city[car].text

            if len(description) > car:
                car_json['description'] = description[car].text

            if car_json['name'] == 'Ошибка':
                print(car_json['link'])

            data.add(json.dumps(car_json))

            cnt += 1

        time.sleep(4)

        if cnt > 0:
            print("Parsed car = " + car_json['name'] + " with time = " + str(time.time() - time1) + " page = " + str(page_idx) + " cnt = " + str(cnt))

        # Переход на следующую страницу
        try:
            next_page = browser.find_element(
                By.XPATH, "//a[contains(@data-marker, "
                            "'pagination-button/next')]")

            next_page.click()
        except:
            break

    return data


def get_parsed_avito(should_parse_big_brands=False, brand_to_start=None, model_to_start=None):
    # Без открытия окна браузера
    options = Options()
    options.add_argument("--headless")

    # Открываем основную страницу поиска авто на Авито
    browser = webdriver.Chrome(options=options)
    browser.get("https://www.avito.ru/moskva_i_mo/avtomobili")

    time.sleep(2)

    if not should_parse_big_brands:
        # Нажимаем кнопку "Все авто"
        all_brands_button = browser.find_element(
            By.XPATH, "//button[contains(@class, 'popular-rubricator-button')]")

        all_brands_button.click()

    print('start parsing')

    # Достаем список брендов-производителей автомобилей,
    # чтобы дальше перейти на страницу отдельного производителя
    brands = browser.find_elements(
        By.XPATH, "//a[contains(@class, 'popular-rubricator-link')]")

    # checker = 1

    for brand in brands:
        brand_name = brand.text
        if brand_to_start is not None and brand_name < brand_to_start:
            print('Skip ' + brand_name)
            continue
        # checker += 1
        page_link = brand.get_attribute('href')

        brand_browser = webdriver.Chrome(options=options)
        brand_browser.get(page_link)

        print("parsing brand")

        time.sleep(5)

        brand_size = brand_browser.find_elements(
            By.XPATH,
            "//span[contains(@data-marker, 'page-title/count')]")

        if not should_parse_big_brands and len(brand_size) > 0 and int(brand_size[0].text.replace(' ', '')) < 5000:
            print("parse by brand", brand_name)
            data = []
            parsed_data = get_by_pages(brand_browser, brand_name)
            parsed_data = predict.convert_dataframe_to_jsons(predict.predict_price(predict.convert_jsons_to_dataframe(parsed_data)))
            for item in parsed_data:
                data.append(json.loads(item))
            print(len(data))
            if len(data) == 0:
                continue
            time.sleep(2)
            upsert_new_market_state.upsert_new_data(data)
            time.sleep(2)
            upsert_new_market_state.move_selled_cars(data, 'avito', brand_name)
            time.sleep(2)
            upsert_new_market_state.move_fake_selled_cars_back(data, 'avito', brand_name)
            brand_browser.close()
            continue
        elif not should_parse_big_brands:
            continue
        elif should_parse_big_brands and len(brand_size) > 0 and int(brand_size[0].text.replace(' ', '')) < 5000:
            continue

        all_models_button = brand_browser.find_elements(
            By.XPATH,
            "//button[contains(@class, 'popular-rubricator-button-WWqUy')]")

        if len(all_models_button) > 0:
            all_models_button[0].click()
        
        time.sleep(1)

        # Достаем список моделей одного производитея автомобилей,
        # чтобы дальше перейти на страницу отдельной модели
        models = brand_browser.find_elements(
            By.XPATH, "//a[contains(@class, 'popular-rubricator-link-Hrkjd')]")

        for model in models:
            model_name = model.text.replace(' ', '')
            if model_to_start is not None and model_name < model_to_start:
                print('Skip model ' + model_name)
                continue
            model_link = model.get_attribute('href')

            time.sleep(4)

            model_browser = webdriver.Chrome(options=options)
            model_browser.get(model_link)

            print("parsing model")

            time.sleep(8)

            data = []
            parsed_data = get_by_pages(model_browser, brand_name)
            for item in parsed_data:
                data.append(json.loads(item))
            print(len(data))
            if len(data) == 0:
                continue
            time.sleep(2)
            upsert_new_market_state.upsert_new_data(data)
            time.sleep(2)
            upsert_new_market_state.move_selled_cars(data, 'avito', brand_name, model_name)
            time.sleep(2)
            upsert_new_market_state.move_fake_selled_cars_back(data, 'avito', brand_name, model_name)

            model_browser.close()

        brand_browser.close()
        # if checker > 1:
        # break

    browser.close()
