from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import pandas as pd
from collections import defaultdict

data = pd.DataFrame(
    {'Name': [], 'Price': [], 'Engine': [], 'Mileage': [], 'BodyType': [],
     'FuelType': [], 'Transmission': [], 'SellerType': [], 'City': [],
     'Description': [], 'Link': [], 'HorsePower': [], 'Color': [],
     'GearBox': [], 'SteeringWheelSide': [], 'DocumentsOK': [],
     'OwnersCounter': [], 'CarIsWanted': [], 'CarIsBusted': []})

browser = webdriver.Chrome()
browser.get("https://moscow.drom.ru/auto/?distance=100")

while True:
    time.sleep(2)

    cars = \
        browser.find_elements(By.XPATH,
                              "//a[contains(@class, 'css-xb5nz8')]")

    for car in cars:
        current = webdriver.Chrome()
        current.get(car.get_attribute('href'))

        time.sleep(2)

        try:
            name = current.find_element(
                By.XPATH, "//h1[contains(@class, 'css-1tjirrw')]").text
        except:
            name = 'Неизвестно'

        try:
            price = current.find_element(
                By.XPATH, "//div[contains(@class, 'css-eazmxc')]").text
        except:
            price = 'Неизвестно'

        try:
            specs_data = current.find_elements(
                By.XPATH, "//td[contains(@class, 'css-9xodgi')]")
            specs_txt = current.find_elements(
                By.XPATH, "//th[contains(@class, 'css-16lvhul')]")

            tmp = dict([(key.text, value.text) for i, (key, value) in
                          enumerate(zip(specs_txt, specs_data))])

            specs = defaultdict(lambda: 'Неизвестно', tmp)

            engine = specs['Двигатель']
            hp = specs['Мощность'].split(',')[0]
            gear = specs['Коробка передач']
            transmission = specs['Привод']
            body = specs['Тип кузова']
            color = specs['Цвет']
            mileage = specs['Пробег, км']
            steering = specs['Руль']
        except:
            engine = 'Неизвестно'
            hp = 'Неизвестно'
            gear = 'Неизвестно'
            transmission = 'Неизвестно'
            body = 'Неизвестно'
            color = 'Неизвестно'
            mileage = 'Неизвестно'
            steering = 'Неизвестно'

        try:
            report = current.find_elements(
                By.XPATH, "//div[contains(@class, 'css-13qo6o5')]")
            documents_ok = report[0].text
            #owners = current.find_element(
                #By.XPATH, "//button[contains(@class, 'e8vftt60')]").text
            owners = report[1].text
            wanted = report[2].text
            busted = report[3].text
        except:
            documents_ok = 'Неизвестно'
            owners = 'Неизвестно'
            busted = 'Неизвестно'
            wanted = 'Неизвестно'

        try:
            full_description_button = current.find_element(
                By.XPATH,
                "//button[contains(@data-ga-stats-name, "
                "'show_full_description')]")

            full_description_button.click()

            description = current.find_elements(
                By.XPATH, "//span[contains(@class, 'css-1kb7l9z')]")[1].text
        except:
            try:
                description = current.find_elements(
                    By.XPATH, "//span[contains(@class, 'css-1kb7l9z')]")[1].text

            except:
                description = 'Неизвестно'

        link = str(current.current_url)

        data.loc[len(data.index)] = [name, price, engine, mileage, body,
                                     "Смотреть в 'Двигатель'", transmission,
                                     "Не указано на Дром", 'Москва и МО',
                                     description, link, hp, color, gear,
                                     steering, documents_ok, owners, wanted,
                                     busted]
        time.sleep(2)
        current.close()

    try:
        next_page = browser.find_element(
            By.XPATH,
            "//a[contains(@data-ftid, 'component_pagination-item-next')]")
        next_page.click()
    except:
        break


browser.close()
data.to_csv('drom.csv')
