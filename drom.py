import upsert_new_market_state
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from collections import defaultdict

class CaptchaException(Exception):
    pass

def parse_item_id_by_link(link):
    link_arr = link.split(sep='/')
    return link_arr[-1][:len(link_arr[-1]) - 5]

def get_parsed_drom(brand_to_start=None):
    options = Options()
    options.add_argument("--headless")

    browser = webdriver.Chrome(options=options)
    browser.get("https://moscow.drom.ru/auto/")

    all_brands_button = browser.find_element(
        By.XPATH, "//div[contains(@class, 'css-atyutb')]")
    all_brands_button.click()

    brands = browser.find_elements(
        By.XPATH, "//a[contains(@data-ftid, 'component_cars-list-item_hidden-link')]")
    
    for brand in brands:
        brand_browser = webdriver.Chrome(options=options)
        print(brand.get_attribute('href'))
        brand_browser.get(brand.get_attribute('href'))

        brand_name = brand.text
        if brand_to_start is not None and brand_name < brand_to_start:
            continue

        data = []
        page_idx = 0
        while True:
            time.sleep(2)

            if page_idx > 100:
                raise CaptchaException(brand_name)

            cars = \
                brand_browser.find_elements(By.XPATH,
                                    "//a[contains(@class, 'css-xb5nz8')]")

            for car in cars:
                time1 = time.time()
                current = webdriver.Chrome(options=options)
                current.get(car.get_attribute('href'))

                time.sleep(2)

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
                    'city': 'Москва',
                    'description': 'Ошибка',
                    'link': 'Ошибка',
                    'market_type': 'drom',
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

                try:
                    car_json['name'] = current.find_element(
                        By.XPATH, "//h1[contains(@class, 'css-1tjirrw')]").text
                    
                    splitted_name = car_json['name'].split(', ')
                    car_json['year'] = int(splitted_name[1].split(' ')[0])
                    splitted_brand_model = splitted_name[0].split(' ')
                    parsed_model_name = ''
                    for idx in range(len(brand_name.split(' ')) + 1, len(splitted_brand_model)):
                        parsed_model_name += splitted_brand_model[idx]
                    car_json['model_name'] = parsed_model_name
                    print(car_json['model_name'])
                except:
                    print('got exception')

                try:
                    car_json['price'] = int(current.find_element(
                        By.XPATH, "//div[contains(@class, 'css-eazmxc')]").text.replace(' ', '')[:-1])
                except:
                    print('got exception')

                try:
                    specs_data = current.find_elements(
                        By.XPATH, "//td[contains(@class, 'css-9xodgi')]")
                    specs_txt = current.find_elements(
                        By.XPATH, "//th[contains(@class, 'css-16lvhul')]")

                    tmp = dict([(key.text, value.text) for i, (key, value) in
                                enumerate(zip(specs_txt, specs_data))])

                    specs = defaultdict(lambda: 'Ошибка', tmp)

                    car_json['fuel_type'] = specs['Двигатель'].split(',')[0]
                    car_json['horse_power'] = int(specs['Мощность'].split(' ')[0])
                    car_json['gear_box'] = specs['Коробка передач']
                    car_json['transmission'] = specs['Привод']
                    car_json['body_type'] = specs['Тип кузова']
                    car_json['color'] = specs['Цвет']
                    car_json['mileage'] = int(specs['Пробег, км'].replace(' ', ''))
                    car_json['steering_wheel_side'] = specs['Руль']
                except:
                    print('got exception')

                try:
                    report = current.find_elements(
                        By.XPATH, "//div[contains(@class, 'css-13qo6o5')]")
                    car_json['documents_ok'] = report[0].text
                    #owners = current.find_element(
                        #By.XPATH, "//button[contains(@class, 'e8vftt60')]").text
                    car_json['owners_counter'] = report[1].text
                    car_json['car_is_wanted'] = report[2].text
                    car_json['car_is_busted'] = report[3].text
                except:
                    print('got exception')

                try:
                    full_description_button = current.find_element(
                        By.XPATH,
                        "//button[contains(@data-ga-stats-name, "
                        "'show_full_description')]")

                    full_description_button.click()

                    car_json['description'] = current.find_elements(
                        By.XPATH, "//span[contains(@class, 'css-1kb7l9z')]")[1].text
                except:
                    try:
                        car_json['description'] = current.find_elements(
                            By.XPATH, "//span[contains(@class, 'css-1kb7l9z')]")[1].text

                    except:
                        print('got exception')

                car_json['link'] = str(current.current_url)
                car_json['item_id'] = parse_item_id_by_link(car_json['link'])

                data.append(car_json)

                print('parsed car ' + car_json['name'] + ' for time ' + str(time.time() - time1))

                time.sleep(2)
                current.close()

            try:
                next_page = brand_browser.find_element(
                    By.XPATH,
                    "//a[contains(@data-ftid, 'component_pagination-item-next')]")
                next_page.click()
                page_idx += 1
            except:
                break

        if len(data) == 0:
            continue

        time.sleep(2)
        upsert_new_market_state.upsert_new_data(data)
        time.sleep(2)
        upsert_new_market_state.move_selled_cars(data, 'drom', brand_name)
        time.sleep(2)
        upsert_new_market_state.move_fake_selled_cars_back(data, 'drom', brand_name)

    browser.close()

brand_to_start = None

while True:
    try:
        get_parsed_drom(brand_to_start)
        brand_to_start = None
    except CaptchaException as e:
        print(e)
        brand_to_start = str(e)
