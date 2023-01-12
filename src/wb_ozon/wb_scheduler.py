import time

import schedule
from wb_parser import main, driver


def run_wb():
    try:
        main()
    except:
        driver.close()
        driver.quit()


schedule.every().minute.do(run_wb)

schedule.run_all()
while True:
    schedule.run_pending()
    time.sleep(5)
