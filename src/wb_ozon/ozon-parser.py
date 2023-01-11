import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
from datetime import datetime
from datetime import timedelta
import locale
import pandas as pd
import json
import re
from datbass.crud import add_cards, add_price, add_rate, add_review, add_seller


def make_url(row: tuple) -> str:
  url = 'https://www.ozon.ru/search/?from_global=true&text=' + f'{row[0]}&brand='
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
  block = driver.find_element(By.XPATH, "//div[contains(text(), 'По запросу')]").text
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
  driver.get(url)
  time.sleep(5)
  driver.find_element(By.XPATH, "//span[contains(text(), 'Все фильтры')]").click()
  time.sleep(4)
  try:
    driver.find_element(By.XPATH, "//span[contains(text(), 'Продавец')]").click()
    time.sleep(1)
  except Exception:
    countShops(driver, url)
  flag = 0
  try:
    driver.find_element(By.XPATH, "//span[contains(text(), 'Продавец')]/../../../../div[2]/div/span").click()
    time.sleep(2)
  except Exception:
    # print("флаг равен 1")
    flag = 1
  if flag == 1:
    shoplist = driver.find_elements(By.XPATH, "//span[contains(text(), 'Продавец')]/../../../../div[2]/div/div/span")
  else: 
    shoplist = driver.find_elements(By.XPATH, "//span[contains(text(), 'Продавец')]/../../../../div[2]/div/div[2]/div/span")
  return len(shoplist)

def takelinks(driver, pages: int, url: str) -> list:
  link_list_uri = []
  link_list = []
  curNumPage = 1
  while curNumPage <= pages:    
    driver.get(f"{url}"+f"&page={curNumPage}")
    time.sleep(5)
    links = driver.find_elements(By.XPATH, "//div[contains(@class, 'widget-search-result-container')]/div/div/div/a")
    if len(links) == 0:
      break
    # print(len(links))
    for link in links:
      link_list.append(link.get_attribute("href").split('?')[0])
      link_list_uri.append(link.get_attribute("href").split('?')[0][19:])
    curNumPage += 1
    link_list_uniq = set(link_list)
  return list(link_list_uniq), link_list_uri

def get_rate(driver, link_list: list) -> dict:
  shopRateList = []
  for link in link_list:
    driver.get(f"{link}")
    time.sleep(3)
    try:
      nameShop = driver.find_element(By.XPATH, "//div[contains(text(), 'родавец')]/../../../../../div[2]//a").get_attribute("title")
      rate = driver.find_element(By.XPATH, "//span[contains(text(), 'рейтинг товаров')]/../span[1]").text
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
  return shopRateList

def get_comment_count_forweek(driver, link_list: list) -> int:
  listDateWeek = makeDateList()    
  commentCount = 0
  for link in link_list:
    numPageCom = 1
    matches = True
    while matches == True:
      currCommentCount = 0
      driver.get(f"{link}" + "reviews/" + f"?page={numPageCom}")
      time.sleep(3)
      dateReviews = driver.find_elements(By.XPATH, "//div[contains(text(), 'Товар куплен на OZON')]/../../../../../div[1]/div[2]/div[1]")
      for el in dateReviews:
        if el.text.lower() in listDateWeek:
          currCommentCount += 1
      if len(dateReviews) != currCommentCount or len(dateReviews) == 0:
        matches = False
      else:
        numPageCom += 1
      commentCount += currCommentCount  
  return commentCount

def parse_data(data: dict) -> dict:
    widgets = data.get('widgetStates')
    for key, value in widgets.items():
        if 'webProductHeading' in key:
            title = json.loads(value).get('title')
        if 'webSale' in key:
            prices = json.loads(value).get('offers')[0]
            if prices.get('price'):
                price = re.search(r'[0-9]+', prices.get('price').replace(u'\u2009', ''))[0]
            else:
                price = 0
            if prices.get('originalPrice'):
                discount_price = re.search(r'[0-9]+', prices.get('originalPrice').replace(u'\u2009', ''))[0]
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
    url = f"https://www.ozon.ru/api/composer-api.bx/page/json/v2?url={link}"
    driver.maximize_window()
    driver.get(url)
    data = driver.find_element(By.TAG_NAME, "pre").get_attribute('innerHTML')
    data = re.sub(";","",data)
    data = json.loads(data)
    data = parse_data(data)
    json_price.append(data)
  return json_price

def main():
  brands = pd.read_excel('brand-test.xlsx')
  brands = brands.drop_duplicates(keep='first')
  
  print("Введите количество страниц карточек товара, с которых необходимо спарсить ссылки...")
  MAX_PAGE = int(input())
  
  for row in brands.itertuples(index=False):
    url = make_url(row) 
    options = uc.ChromeOptions()
    options.headless=True
    options.add_argument('--headless')
    driver = uc.Chrome(options=options)
    try:
      # driver.execute_script("window.scrollTo(5,40000);")
      # time.sleep(3)
    
      print("Считаем кол-во карточек товара по всем страницам...")
      countCardsItem = countCards(driver, url)
      add_cards(row[0], countCardsItem, 'ozon')
      print("Считаем кол-во продавцов по всем страницам...") 
      countShopsProd = countShops(driver, url)
      add_seller(row[0], countShopsProd, 'ozon')
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
      for item in price_list:
        add_price(row[0], item["brand"], item["price"], 'ozon')
      # with open('product_links'+'.txt', 'w', encoding='utf-8') as f:
      #   for link in link_list:
      #       f.write(link + '\n')

      print("Получаем рейтинги продавцов...")
      shopRatingList = get_rate(driver, link_list)
      for item in shopRatingList:
        add_rate(row[0], item['shopname'], item['rate'], 'ozon')
      # with open(f'{row[0]}'+'.txt', 'a', encoding='utf-8') as f:
      #   for i in shopRatingList:
      #       f.write(i + '\n')

      print("Считаем количество отзывов за неделю...")
      commentsCount = get_comment_count_forweek(driver, link_list)
      add_review(row[0], commentsCount, 'ozon')
      print("Количество отзывов за неделю:", commentsCount)
      
      
      list_metric = []
      list_metric.append({'countCards':countCardsItem, 'countShops':countShopsProd,\
        'price':price_list, 'rate':shopRatingList, 'countRev':commentsCount})
      
      with open(f'ozon_data{row[0]}.json', 'w', encoding='UTF-8') as file:
        json.dump(list_metric, file, indent=2, ensure_ascii=False)
        print(f'Данные сохранены в ozon_data{row[0]}.json')
      
      
      
      # with open(f"{row[0]}"+".txt", "a", encoding='utf-8') as file:
      #   file.write(f"\nКоличество отзывов за неделю: {commentsCount}")
    
      # time.sleep(3)
    except Exception as ex:
      print(ex)
      main()
    
  driver.close()  
  driver.quit()

if __name__ == '__main__':
    main()