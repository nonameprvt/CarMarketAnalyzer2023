import upsert_new_market_state
from avito import get_parsed_avito
import schedule
import time

def update_avito_db():
    data = get_parsed_avito()
    time.sleep(2)
    upsert_new_market_state.move_selled_cars(data, 'avito')
    time.sleep(2)
    upsert_new_market_state.upsert_new_data(data)

schedule.every().day.at("20:02").do(update_avito_db)

while True:
    schedule.run_pending()
    time.sleep(1)
