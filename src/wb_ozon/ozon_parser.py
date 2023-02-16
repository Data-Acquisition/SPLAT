import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime, date
from datetime import timedelta
import locale
import pandas as pd
import json
import re
from datbass.crud import add_cards, add_price, add_rate, add_review, add_seller
import requests

driver = None


def send_message_tg(message):
    bot_token = '5901249206:AAFXkWy3OpRGS9RY1ST0zooUI4uVyi51xzM'
    chat_id = '-1001504854026'
    # chat_id = '369056839'
    send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + message
    response = requests.post(send_text)
    print(response.json())


def make_url(row: tuple) -> str:
    url = 'https://www.ozon.ru/search/?from_global=true&text=' + \
        f'{row[0]}&brand='
    for i in range(1, len(row)):
        if pd.isna(row[i]):
            continue
        else:
            j = row[i]
            if type(j) == float:
                j = int(j)
            j = str(j)
            if i == 1:
                url += j
            else:
                url += '%2C' + j
    return url


def makeDateList() -> list:
    listDate = []
    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
    now = datetime.now()
    day = 0
    while day != 7:
        if (now - timedelta(day)).strftime("%d %B %Y")[0] == "0":
            listDate.append((now - timedelta(day)).strftime("%d %B %Y")[1:])
        else:
            listDate.append((now - timedelta(day)).strftime("%d %B %Y"))
        day += 1
    return listDate


def countCards(driver, url) -> int:
    driver.get(url)
    time.sleep(5)
    block = driver.find_element(
        By.XPATH, "//div[contains(text(), 'По запросу')]").text
    block = block[::-1]
    countItems = ""
    for el in block:
        if el != 'н':
            if el.isdigit():
                countItems += el
        else:
            break
    countItems = countItems[::-1]
    return int(countItems)


def countShops(driver, url) -> int:
    print(url)
    driver.get(url)
    time.sleep(5)
    try:
      driver.find_element(
          By.XPATH, "//span[contains(text(), 'Все фильтры')]").click()
      time.sleep(4)
    except Exception as ex:
      print(ex)
      countShops(driver, url)
    try:
        driver.find_element(
            By.XPATH, "//span[contains(text(), 'Продавец')]").click()
        time.sleep(1)
    except Exception as ex:
        print(ex)
        countShops(driver, url)
    flag = 0
    try:
        driver.find_element(
            By.XPATH, "//span[contains(text(), 'Продавец')]/../../../../div[2]/div/span").click()
        time.sleep(2)
    except Exception:
        # print("флаг равен 1")
        flag = 1
    if flag == 1:
        shoplist = driver.find_elements(By.XPATH,
                                        "//span[contains(text(), 'Продавец')]/../../../../div[2]/div/div/span")
    else:
        shoplist = driver.find_elements(By.XPATH,
                                        "//span[contains(text(), 'Продавец')]/../../../../div[2]/div/div[2]/div/span")
    return len(shoplist)


def takelinks(driver, pages: int, url: str) -> list:
    # print(url)
    link_list_uri = []
    link_list = []
    curNumPage = 1
    while curNumPage <= pages:
        urll = f"{url}" + f"&page={curNumPage}"
        driver.get(urll)
        time.sleep(5)
        links = driver.find_elements(By.XPATH,
                                     "//div[contains(@class, 'widget-search-result-container')]/div/div/div/a")
        print(len(links))
        if len(links) == 0:
            break
        # print(len(links))
        for link in links:
            link_list.append(link.get_attribute("href").split('?')[0])
            link_list_uri.append(link.get_attribute("href").split('?')[0][19:])
        curNumPage += 1
    link_list_uniq = set(link_list)
    link_list_uri_uniq = set(link_list_uri)
    print(len(link_list_uniq), len(link_list_uri_uniq))
    return list(link_list_uniq), list(link_list_uri_uniq)


def get_rate(driver, link_list: list):
    shopRateList = []
    unit_list = []
    for link in link_list:
        # print(f"{link}")
        driver.get(f"{link}")
        print(f"Success {link}")
        time.sleep(3)
        unit_list.append({'sku':link[-10:-1],
                          'units': get_add_character(driver)})
        # print(unit_list[0])
        try:
            nameShop = driver.find_element(By.XPATH,
                                           "//div[contains(text(), 'родавец')]/../../../../../div[2]//a").get_attribute(
                "title")
            rate = driver.find_element(
                By.XPATH, "//span[contains(text(), 'рейтинг товаров')]/../span[1]").text
            rateNew = ''
            for ch in rate:
                if ch == ',':
                    rateNew += '.'
                else:
                    rateNew += ch
            shopRateList.append({
                'shopname': str(nameShop),
                'rate': float(rateNew[:3])})
        except Exception:
            continue
        # time.sleep(3)
        

          # continue 
        
    uniq_list_rate = []
    for item in shopRateList:
      if item not in uniq_list_rate:
        uniq_list_rate.append(item)  
       
    return uniq_list_rate, unit_list

def get_add_character(driver):
  unit_list = []
  try:
    unit = driver.find_element(By.XPATH,
                                    "//span[contains(text(), 'Вес товара')]/../../dd/..//span").text
    unit = unit.split(',')[1][1:]
    unit_measure = driver.find_element(By.XPATH,
                                    "//span[contains(text(), 'Вес товара')]/../../dd").text
    unit_list.append(unit_measure)
    unit_list.append(unit)
  except Exception:
    unit_list.append('')
    unit_list.append('')
  return unit_list

def get_comment_count_forweek(driver, link_list: list) -> int:
    listDateWeek = makeDateList()
    commentCount = 0
    for link in link_list:
      try:
        numPageCom = 1
        matches = True
        while matches == True:
            currCommentCount = 0
            driver.get(f"{link}" + "reviews/" + f"?page={numPageCom}")
            time.sleep(3)
            dateReviews = driver.find_elements(By.XPATH,
                                               "//div[contains(text(), 'Товар куплен на OZON')]/../../../../../div[1]/div[2]/div[1]")
            for el in dateReviews:
                if el.text.lower() in listDateWeek:
                    currCommentCount += 1
            if len(dateReviews) != currCommentCount or len(dateReviews) == 0:
                matches = False
            else:
                numPageCom += 1
            commentCount += currCommentCount
      except Exception:
        continue
    return commentCount


def parse_data(data: dict) -> dict:
    widgets = data.get('widgetStates')
    for key, value in widgets.items():
        if 'webProductHeading' in key:
            title = json.loads(value).get('title')
        if 'webSale' in key:
            prices = json.loads(value).get('offers')[0]
            if prices.get('price'):
                price = re.search(
                    r'[0-9]+', prices.get('price').replace(u'\u2009', ''))[0]
            else:
                price = 0
            if prices.get('originalPrice'):
                discount_price = re.search(
                    r'[0-9]+', prices.get('originalPrice').replace(u'\u2009', ''))[0]
            else:
                discount_price = 0

    layout = json.loads(data.get('layoutTrackingInfo'))
    brand = layout.get('brandName')
    category = layout.get('categoryName')
    sku = layout.get('sku')
    url = layout.get('currentPageUrl')

    product = {
        'title': title,
        'price': price,
        'discount_price': discount_price,
        'brand': brand,
        'category': category,
        'sku': sku,
        'url': url
    }
    return product


def get_price(driver, uri) -> dict:
    json_price = []
    for link in uri:
      try:
        url = f"https://www.ozon.ru/api/composer-api.bx/page/json/v2?url={link}"
        # print(url)
        driver.maximize_window()
        driver.get(url)
        data = driver.find_element(
            By.TAG_NAME, "pre").get_attribute('innerHTML')
        data = re.sub(";", "", data)
        data = json.loads(data)
        # print(data)
        with open('ozon_data.json', 'w', encoding='UTF-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        data = parse_data(data)
        json_price.append(data)
      except Exception:
        continue
    print(len(json_price))
    uniq_price_list = []
    for item in json_price:
      if item not in uniq_price_list:
        uniq_price_list.append(item)
    print(len(uniq_price_list))
    return uniq_price_list


def main():
    global driver
    brands = pd.read_excel('brand-id-ozon.xlsx')
    brands = brands.drop_duplicates(keep='first')

    print("Введите количество страниц карточек товара, с которых необходимо спарсить ссылки...")
    MAX_PAGE = 1

    for row in brands.itertuples(index=False):
        url = make_url(row)
        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument(f'--disable-notifications')
        options.add_argument(f'--no-first-run --no-service-autorun --password-store=basic')
        options.add_argument(f'--disable-gpu')
        options.add_argument(f'--disable-dev-shm-usage')
        options.add_argument(f'--no-sandbox')
        driver = uc.Chrome(options=options, service=Service(ChromeDriverManager().install()))
        # time.sleep(2)
        try:
            # driver.execute_script("window.scrollTo(5,40000);")
            # time.sleep(3)

            print("Считаем кол-во карточек товара по всем страницам...")
            countCardsItem = countCards(driver, url)
            print(countCardsItem)
            add_cards(row[0], countCardsItem, 'ozon', date.today())
            
            print("Считаем кол-во продавцов по всем страницам...")
            countShopsProd = countShops(driver, url)
            add_seller(row[0], countShopsProd, 'ozon', date.today())
            
            
            # print("Количество карточек товара:", countCardsItem, "\nКоличество продавцов:", countShopsProd)

            # with open(f"{row[0]}"+".txt", "w", encoding='utf-8') as file:
            #   file.write(f"Количество карточек товара: {countCardsItem}\n")
            #   file.write(f"Количество продавцов: {countShopsProd}\n\n")

            # with open("shoplist"+".txt", "w", encoding='utf-8') as file:
            #   for el in countShopsProd:
            #     file.write(f"{el.text}\n")

            print("Получаем ссылки карточек...")
            link_list, link_list_uri = takelinks(driver, MAX_PAGE, url)

            print("Получаем цену на товары...")
            price_list = get_price(driver, link_list_uri)
            # print(price_list)
            # with open('product_links'+'.txt', 'w', encoding='utf-8') as f:
            #   for link in link_list:
            #       f.write(link + '\n')

            print("Получаем рейтинги продавцов...")
            shopRatingList, unit_list = get_rate(driver, link_list)
            for item in shopRatingList:
              try:
                add_rate(row[0], item['shopname'], item['rate'], 'ozon', date.today())
              except Exception:
                continue
            # with open(f'{row[0]}'+'.txt', 'a', encoding='utf-8') as f:
            #   for i in shopRatingList:
            #       f.write(i + '\n')
            # countUnit = 0
            # print(len(unit_list))
            # print(len(price_list))
            for item in price_list:
              for units in unit_list:
                if item['sku'] == int(units['sku']):
                  add_price(item['sku'] ,row[0], item["title"], item["price"], 'ozon',
                            date.today(), units['units'][0], units['units'][1], item["brand"])
                  continue
                # countUnit += 1
            


            print("Считаем количество отзывов за неделю...")
            commentsCount = get_comment_count_forweek(driver, link_list)
            add_review(row[0], commentsCount, 'ozon', date.today())
            print("Количество отзывов за неделю:", commentsCount)

            # list_metric = []
            # list_metric.append({'countCards': countCardsItem, 'countShops': countShopsProd,
            #                     'price': price_list, 'rate': shopRatingList, 'countRev': commentsCount})

            # with open(f'ozon_data{row[0]}.json', 'w', encoding='UTF-8') as file:
            #     json.dump(list_metric, file, indent=2, ensure_ascii=False)
            #     print(f'Данные сохранены в ozon_data{row[0]}.json')

            # with open(f"{row[0]}"+".txt", "a", encoding='utf-8') as file:
            #   file.write(f"\nКоличество отзывов за неделю: {commentsCount}")

            # time.sleep(3)
        except Exception as ex:
            print(ex)
            send_message_tg(str(ex))
            main()

        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
