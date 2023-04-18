from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.chrome.options import Options

# Создаем хранилище данных авто
data = pd.DataFrame(
    {'Name': [], 'Price': [], 'Engine': [], 'Mileage': [], 'BodyType': [],
     'FuelType': [], 'Transmission': [], 'SellerType': [], 'City': [],
     'Description': [], 'Link': []})

# Без открытия окна браузера
options = Options()
options.add_argument("--headless")

# Открываем основную страницу поиска авто на Авито
browser = webdriver.Chrome(options=options)
browser.get("https://www.avito.ru/moskva_i_mo/avtomobili")

# Нажимаем кнопку "Все авто"
all_brands_button = browser.find_element(
    By.XPATH, "//button[contains(@class, 'popular-rubricator-button')]")

all_brands_button.click()

# Достаем список брендов-производителей автомобилей,
# чтобы дальше перейти на страницу отдельного производителя
brands = browser.find_elements(
    By.XPATH, "//a[contains(@class, 'popular-rubricator-link')]")

# checker = 1

for brand in brands:
    # checker += 1
    page_link = brand.get_attribute('href')

    brand_browser = webdriver.Chrome(options=options)
    brand_browser.get(page_link)

    all_models_button = brand_browser.find_elements(
        By.XPATH,
        "//button[contains(@class, 'popular-rubricator-button-WWqUy')]")

    if len(all_models_button) > 0:
        all_models_button[0].click()

    # Достаем список моделей одного производитея автомобилей,
    # чтобы дальше перейти на страницу отдельной модели
    models = brand_browser.find_elements(
        By.XPATH, "//a[contains(@class, 'popular-rubricator-link-Hrkjd')]")

    for model in models:
        model_link = model.get_attribute('href')

        model_browser = webdriver.Chrome(options=options)
        model_browser.get(model_link)

        while True:
            # Проверяем, есть ли автомобили на этой странице.
            check_no_results = False
            try:
                no_results_title = model_browser.find_element(
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
                if len(params[car].text.split(', ')) > 4:
                    specs = params[car].text.split(', ')
                    mileage, engine, body, transmission, fuel = \
                        specs[0], specs[1], specs[2], specs[3], specs[4]
                else:
                    mileage, engine, body, transmission, fuel = \
                        'Ошибка', 'Ошибка', 'Ошибка', 'Ошибка', 'Ошибка'

                if len(name) > car:
                    car_name = name[car].text
                else:
                    car_name = 'Ошибка'

                if len(price) > 2 * car + 1:
                    car_price = price[2 * car + 1].get_attribute('content')
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
                    car_link = link[car].get_attribute('href')
                else:
                    car_link = 'Ошибка'

                data.loc[len(data.index)] = [car_name, car_price, engine, mileage,
                                             body,
                                             fuel, transmission, car_seller,
                                             car_city,
                                             car_description, car_link]

            time.sleep(2)

            # Переход на следующую страницу
            try:
                next_page = model_browser.find_element(
                    By.XPATH, "//a[contains(@data-marker, "
                              "'pagination-button/next')]")

                next_page.click()
            except:
                break

        model_browser.close()

    brand_browser.close()
    #if checker > 1:
        #break

browser.close()
data.to_csv('avito.csv')
