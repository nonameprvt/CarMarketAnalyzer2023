from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import pandas as pd


def parse_item_id_by_link(link):
    link_arr = link.split(sep='_')
    return link_arr[-1]


def get_parsed_avito():
    data = []

    browser = webdriver.Chrome()
    browser.get("https://www.avito.ru/moskva_i_mo/avtomobili")

    all_cars_button = browser.find_element(
        By.XPATH, "//button[contains(@class, 'popular-rubricator-button')]")

    all_cars_button.click()

    models = browser.find_elements(
        By.XPATH, "//a[contains(@class, 'popular-rubricator-link')]")

    checker = 1

    for model in models:
        page_link = model.get_attribute('href')

        model_browser = webdriver.Chrome()
        model_browser.get(page_link)

        while True:
            check_no_results = False
            try:
                no_results_title = model_browser.find_elements(
                    By.XPATH, "//h2[contains(@class, 'no-results-title')]")
            except:
                check_no_results = True

            if not check_no_results:
                break

            time.sleep(2)

            name = model_browser.find_elements(By.XPATH,
                                            "//h3[contains(@itemprop, 'name')]")
            # достаем -> .text
            price = model_browser.find_elements(
                By.XPATH, "//meta[contains(@itemprop, 'price')]")
            # достаем четные элементы, там цена. В нечетных RUB
            params = model_browser.find_elements(
                By.XPATH, "//div[contains(@data-marker, 'item-specific-params')]")
            # достаем -> .text.split(', '), получаем массив характеристик
            description = model_browser.find_elements(
                By.CLASS_NAME, "iva-item-descriptionStep-C0ty1")
            # достаем -> .text
            seller = model_browser.find_elements(
                By.XPATH, "//div[contains(@data-marker, 'item-line')]")
            # достаем -> .text
            city = model_browser.find_elements(
                By.XPATH, "//div[contains(@class, 'geo-georeferences')]")
            # достаем -> .text
            link = model_browser.find_elements(
                By.XPATH, "//a[contains(@data-marker, 'item-title')]")
            # достаем -> .get_attribute('href')
            time.sleep(2)

            for car in range(len(name)):
                car_json = {
                    'item_id': 'Ошибка',
                    'name': 'Ошибка',
                    'price': 'Ошибка',
                    'engine': 'Ошибка',
                    'mileage': 'Ошибка',
                    'body_type': 'Ошибка',
                    'fuel_type': 'Ошибка',
                    'transmission': 'Ошибка',
                    'seller_type': 'Ошибка',
                    'city': 'Ошибка',
                    'description': 'Ошибка',
                    'link': 'Ошибка',
                }

                if len(params[car].text.split(', ')) > 4:
                    specs = params[car].text.split(', ')
                    car_json['mileage'] = specs[0]
                    car_json['engine'] = specs[1]
                    car_json['body_type'] = specs[2]
                    car_json['transmission'] = specs[3]
                    car_json['fuel_type'] = specs[4]

                if len(name) > car:
                    car_json['name'] = name[car].text

                if len(price) > 2 * car + 1:
                    car_json['price'] = price[2 * car + 1].get_attribute('content')

                if len(seller) > car:
                    car_json['seller_type'] = seller[car].text

                if len(city) > car:
                    car_json['city'] = city[car].text

                if len(description) > car:
                    car_json['description'] = description[car].text

                if len(link) > car:
                    car_json['link'] = link[car].get_attribute('href')

                car_json['item_id'] = parse_item_id_by_link(car_json['link'])

                data.append(car_json)

            time.sleep(2)
            try:
                next_page = model_browser.find_element(
                    By.XPATH, "//a[contains(@data-marker, "
                            "'pagination-button/next')]")

                next_page.click()
            except:
                break

        model_browser.close()

    browser.close()
    return data
