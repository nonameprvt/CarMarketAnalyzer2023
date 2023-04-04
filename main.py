from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import pandas as pd

data = pd.DataFrame(
    {'Name': [], 'Price': [], 'Engine': [], 'Mileage': [], 'BodyType': [],
     'FuelType': [], 'Transmission': [], 'SellerType': [], 'City': [],
     'Description': [], 'Link': []})

browser = webdriver.Chrome()
browser.get("https://www.avito.ru/all/avtomobili?cd=1")

for page in range(1, 6):
    time.sleep(2)

    name = browser.find_elements(By.XPATH,
                                 "//h3[contains(@itemprop, 'name')]")
    # достаем -> .text
    price = browser.find_elements(By.XPATH,
                                  "//meta[contains(@itemprop, 'price')]")
    # достаем четные элементы, там цена. В нечетных RUB
    params = browser.find_elements(By.XPATH,
                                   "//div[contains(@data-marker, "
                                   "'item-specific-params')]")
    # достаем -> .text.split(', '), получаем массив характеристик
    description = browser.find_elements(By.CLASS_NAME,
                                        "iva-item-descriptionStep-C0ty1")
    # достаем -> .text
    seller = browser.find_elements(By.XPATH,
                                   "//div[contains(@data-marker, 'item-line')]")
    # достаем -> .text
    city = browser.find_elements(By.XPATH,
                                 "//div[contains(@class, 'geo-address')]")
    # достаем -> .text
    link = browser.find_elements(By.XPATH,
                                 "//a[contains(@data-marker, 'item-title')]")
    # достаем -> .get_attribute('href')
    time.sleep(2)

    for car in range(len(name)):
        if len(params[car].text.split(', ')) > 4:
            mileage, engine, body, transmission, fuel = \
                params[car].text.split(', ')
        else:
            mileage, engine, body, transmission, fuel = 'Ошибка', 'Ошибка', \
                                                        'Ошибка', 'Ошибка', \
                                                        'Ошибка'
        if len(name) > car:
            car_name = name[car].text
        else:
            car_name = 'Ошибка'

        if len(price) > 2 * car + 1:
            car_price = price[car].get_attribute('content')
        else:
            car_price = 'Ошибка'

        if len(seller) > car:
            car_seller = seller[car].text
        else:
            car_seller = 'Ошибка'

        if len(city) > car:
            car_city = city[car].text
        else:
            car_city = 'Ошибка'

        if len(description) > car:
            car_description = description[car].text
        else:
            car_description = 'Ошибка'

        if len(link) > car:
            car_link = link[car].text
        else:
            car_link = 'Ошибка'

        data.loc[len(data.index)] = [car_name, car_price, engine, mileage, body,
                                     fuel, transmission, car_seller, car_city,
                                     car_description, car_link]

    time.sleep(2)
    next_page = \
        browser.find_element(By.XPATH,
                             "//span[contains(@data-marker, "
                             "'pagination-button/next')]")
    next_page.click()

browser.close()
data.to_csv('avito.csv')
