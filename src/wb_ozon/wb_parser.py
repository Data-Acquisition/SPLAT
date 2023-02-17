import pandas as pd
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datbass.crud import add_cards, add_price, add_rate, add_review, add_seller
import time
from datetime import datetime, date
from datetime import timedelta
import locale
import json

driver = None


def send_message_tg(message):
    bot_token = '5901249206:AAFXkWy3OpRGS9RY1ST0zooUI4uVyi51xzM'
    chat_id = '-1001504854026'
    # cha_id = '369056839'
    send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + message
    response = requests.post(send_text)
    print(response.json())


def makeDateList() -> list:
    listDate = []
    locale.setlocale(locale.LC_ALL)
    now = datetime.now()
    day = 0
    while day != 7:
        if (now - timedelta(day)).strftime("%Y-%m-%d")[0] == "0":
            listDate.append((now - timedelta(day)).strftime("%Y-%m-%d")[1:])
        else:
            listDate.append((now - timedelta(day)).strftime("%Y-%m-%d"))
        day += 1
    return listDate


def make_url(row: tuple) -> str:
    url1 = f'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-2162196,-1257786&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query={row[0]}&reg=0&regions=80,64,83,4,38,33,70,69,86,75,30,40,48,1,66,31,68,22,71&resultset=filters&spp=0&suppressSpellcheck=false&fbrand='
    url2 = f'https://search.wb.ru/exactmatch/ru/common/v4/search?filters=fsupplier&query={row[0]}&resultset=filters&suppressSpellcheck=false&spp=0&regions=80,64,83,4,38,33,70,69,86,75,30,40,48,1,66,31,68,22,71&pricemarginCoeff=1.0&reg=0&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=12,3,18,15,21&dest=-1029256,-102269,-2162196,-1257786&fbrand='
    url3 = f'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,7,3,6,18,22,21&curr=rub&dest=-1075831,-79374,-367666,-2133462&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query={row[0]}&reg=0&regions=80,64,83,4,38,33,70,69,86,30,40,48,1,66,31,68,22&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false&fbrand='
    for i in range(1, len(row)):
        if pd.isna(row[i]):
            continue
        else:
            j = row[i]
            if type(j) == float:
                j = int(j)
            j = str(j)
            if i == 1:
                url1 += j
                url2 += j
                url3 += j
            else:
                url1 += '%3B' + j
                url2 += '%3B' + j
                url3 += '%3B' + j
    return url1, url2, url3


def get_content(url):
    headers = {'Accept': "*/*",
               'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=headers)
    data = r.json()
    return data


def get_count_cards(json_file):
    return json_file['data']['total']


def get_count_sellers(json_file):
    return len(json_file['data']['filters'][0]['items'])


def get_rate_sellers(json_file, driver):
    data_list = []
    list_rate = []
    for data in json_file['data']['filters'][0]['items']:
        data_list.append(data['id'])
    print(data_list)
    for id in data_list:
      try:
        driver.get(f"https://www.wildberries.ru/seller/{id}")
        time.sleep(1)
        try:
            rating = driver.find_element(
                By.CLASS_NAME, "address-rate-mini").text
        except Exception:
            print(f"не получилось собрать rate idShop: {id}")
            continue
        list_rate.append({
            'idShop': str(id),
            'rate': float(rating)})
      except Exception as ex:
        continue
    uniq_list_rate = []
    for item in list_rate:
      if item not in uniq_list_rate:
        uniq_list_rate.append(item)
    return uniq_list_rate


def get_content_root(url):
    headers = {'Accept': "*/*",
               'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    data_list = []
    list_price = []
    for page in range(1, 101):
      print(f'Сбор позиций со страницы {page} из 100')
      url += f'&page={page}'
      r = requests.get(url, headers=headers)
      json_file = r.json()
      # if page == 1:
      #   print(url)
      #   with open('wb_data.json', 'w', encoding='UTF-8') as file:
      #     json.dump(json_file, file, indent=2, ensure_ascii=False)
      root_list = []
      for data in json_file['data']['products']:
          print(data['id'])
          unit = get_add_character(data['id'])
          # print(unit[0])
          # print(unit[1])
          root_list.append(data['root'])
          list_price.append({'id': data['id'],
                            'idShop': str(data['supplierId']),
                            'brand': data['brand'],
                            'price': float(data['salePriceU'])/100,
                            'unit': unit[0],
                            'unit_measure': unit[1]})
      print(f'Добавлено позиций: {len(root_list)}')
      if len(root_list) > 0:
          data_list.extend(root_list)
      else:
          print(f'Сбор данных завершен.')
          break
    data_list_uniq = set(data_list)
    uniq_list_price = []
    for item in list_price:
      if item not in uniq_list_price:
        uniq_list_price.append(item)
    return list(data_list_uniq), uniq_list_price

def get_add_character(id) -> list:
    id = str(id)
    unit = []
    # characters = {}
    json_file = ''
    headers = {'Accept': "*/*",
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for i in range(1, 11):
        url = ''
        if i <= 9:
            url = f"https://basket-0{i}.wb.ru/vol{id[:-5]}/part{id[:-3]}/{id}/info/ru/card.json"
        else:
            url = f"https://basket-{i}.wb.ru/vol{id[:-5]}/part{id[:-3]}/{id}/info/ru/card.json"
        
        if requests.get(url, headers=headers):
            r = requests.get(url, headers=headers)
            json_file = r.json()
            print(url)
            with open('wb_catalogs_data.json', 'w', encoding='UTF-8') as file:
                    json.dump(json_file, file, indent=2, ensure_ascii=False)
            break 
    for row in json_file['options']:
        if 'Вес товара с упаковкой' in row['name']:
            unit = row['value'].split()
            # print(unit)
            return unit
        elif 'Объем товара' in row['name']:
            unit = row['value'].split()
            return unit
        elif 'Комплектация' in row['name']:
            for i in row['value']:
              if i.isdigit():
                unit = [i] + ['шт']
                return unit
    else:
      return ['', '']

def get_count_review_for_week(data_root: list, dateList: list):
    headers = {'Accept': "*/*",
               'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    count_reviews = 0
    for data in data_root:
        url = f'https://feedbacks1.wb.ru/feedbacks/v1/{data}'
        r = requests.get(url, headers=headers)
        json_file = r.json()
        try:
            for date in range(len(json_file['feedbacks'])):
                create_date = json_file['feedbacks'][date]['createdDate'][:10]
                if create_date in dateList:
                    count_reviews += 1
        except:
            continue
    return count_reviews


def main():
    global driver
    brands = pd.read_excel('brand-id-wb.xlsx')
    brands = brands.drop_duplicates(keep='first')

    try:
        for row in brands.itertuples(index=False):
            options = uc.ChromeOptions()
            options.headless = True
            options.add_argument('--headless')
            options.add_argument('--headless')
            options.add_argument(f'--disable-notifications')
            options.add_argument(f'--no-first-run --no-service-autorun --password-store=basic')
            options.add_argument(f'--disable-gpu')
            options.add_argument(f'--disable-dev-shm-usage')
            options.add_argument(f'--no-sandbox')
            driver = uc.Chrome(options=options, service=Service(ChromeDriverManager().install()))
            print(row[0])
            list_metric = []
            url_cards, url_sellers, url_reviews = make_url(row)
            print('Парсим цены...')
            list_root, list_price= get_content_root(url_reviews)
            for item in list_price:
                add_price(item['id'], row[0], item['idShop'], item['price'], 'wb',
                          date.today(), item['unit'], item['unit_measure'], item['brand'])

            print('Считаем кол-во карточек товара...')
            countCards = get_count_cards(get_content(url_cards))
            add_cards(row[0], countCards, 'wb', date.today())

            print('Считаем кол-во продавцов...')
            countSellers = get_count_sellers(get_content(url_sellers))
            add_seller(row[0], countSellers, 'wb', date.today())

            print('Парсим рейтинги продавцов...')
            rateShops = get_rate_sellers(get_content(url_sellers), driver)
            print('добавляем в базу')
            for item in rateShops:
              try:
                add_rate(row[0], item['idShop'], item['rate'], 'wb', date.today())
              except Exception:
                continue
            print('Считаем комментарии за неделю...')
            countRev = get_count_review_for_week(list_root, makeDateList())
            add_review(row[0], countRev, 'wb', date.today())

            # print('Записываем в json')
            # list_metric.append({'count_cards': countCards,
            #                     'count_sellers': countSellers,
            #                     'rate_sellers_id': rateShops,
            #                     'count_rev': countRev,
            #                     'price': list_price})

            # with open(f'wb_data{row[0]}.json', 'w', encoding='UTF-8') as file:
            #     json.dump(list_metric, file, indent=2, ensure_ascii=False)
            #     print(f'Данные сохранены в wb_data{row[0]}.json')
            driver.close()
            driver.quit()
    except Exception as ex:
        send_message_tg(str(ex))
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
