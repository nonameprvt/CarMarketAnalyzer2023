from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import pandas as pd

data = pd.DataFrame(
    {'Name': [], 'Price': [], 'Engine': [], 'Mileage': [], 'BodyType': [],
     'FuelType': [], 'Transmission': [], 'SellerType': [], 'City': [],
     'Description': [], 'Link': []})

browser = webdriver.Chrome()
browser.get("https://auto.drom.ru/all/")

for page in range(1, 1):
    time.sleep(2)

    #name = browser.find_elements(By.XPATH,
    #                             "//span[contains(@data-ftid, 'bull_title')]")

    #params = browser.find_elements(By.XPATH,
    #                             "//span[contains(@class, 'css-1l9tp44')]")

    #price = browser.find_elements(By.XPATH,
    #                             "//span[contains(@data-ftid, 'bull_price')]")

    #city = browser.find_elements(
    #    By.XPATH, "//span[contains(@data-ftid, 'bull_location')]")

    time.sleep(2)

    next_page = \
        browser.find_elements(By.XPATH,
                              "//a[contains(@class, 'css-xb5nz8')]")

    next_page[0].click()

browser.close()
#data.to_csv('avito.csv')
