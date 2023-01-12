import time

import schedule
from ozon_parser import main, driver

def run_ozon(): 
    try:
        main()
    except:
        driver.close()
        driver.quit()

schedule.every().minute.do(run_ozon)

schedule.run_all()
while True:
    schedule.run_pending()
    time.sleep(5)
