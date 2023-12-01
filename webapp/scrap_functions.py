from bs4 import BeautifulSoup
from selenium import webdriver
import re
import pymorphy2

# options driver
options = webdriver.FirefoxOptions()
# options.add_argument('--headless')

# site
recipe_site = 'https://www.gastronom.ru'
items_site = 'https://online.metro-cc.ru'
recipe_site_search = 'https://www.gastronom.ru/search/type/recipe?t={}'
items_site_search = 'https://online.metro-cc.ru/search?q={}'

# regex
regex = (
    r'больш[а-я][а-я]|средн[а-я][а-я]|зубчик[а-я][*]'
    r'|сваренн[а-я]+|л\.|\d|'
    r'(\bл\b|\bкг\b|\bст\b|\bшт\b|\bг\b|\bгр\b|\bмл\b)|[/.|]|[/–]|'
    r'банка|категор[а-я][а-я]|пучок|%|\bпо\b|\bвкусу\b|\bвашему\b'
)

# morph
morph = pymorphy2.MorphAnalyzer()


def get_bsObj(url: str, time=10):
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    # driver.implicitly_wait(1)
    html = driver.execute_script("return document.body.innerHTML")
    driver.quit()
    return BeautifulSoup(html, 'html.parser')


def get_recipe_by_request(query: str) -> list:
    bsObj = get_bsObj(recipe_site_search.format(query))
    found_goods = bsObj.find_all('article', {'class': 'material-anons col-sm-4 col-ms-6'})

    all_goods = []
    tmp = 0
    for good in found_goods:
        href = good.find('a', {'class': 'material-anons__title'}, href=True)
        if href or tmp != 30:
            all_goods.append((href['href'], href.contents[0]))
        else:
            break
        tmp += 1
    return all_goods


def get_recipies_by_url(url: str):
    '''
    :param url:
    use url that gave you get_recipe_by_request()\n
    use make_readable() on recipe to use get_price_of_ingredient()\n
    :return: recipe
    '''
    bsObj = get_bsObj(recipe_site + url)
    found_goods = bsObj.find_all('li', {'class': 'recipe__ingredient'})

    recipe = []

    for good in found_goods:
        recipe.append(good.contents[0])

    return recipe


def get_price_of_ingredient(ingredient: str) -> tuple[int, str]:
    bsObj = get_bsObj(items_site_search.format(ingredient))
    print("[INFO] get html from items_site")
    helper = 'catalog-2-level-product-card product-card page-search__products-item with-rating with-prices-drop'
    found_goods = bsObj.find_all('div', {'class': helper})

    min_price = 1e10
    min_title = ''

    for good in found_goods:
        price = good.find('span', {'class': 'product-price__sum-rubles'})
        title = good.find('span', {'class': 'product-card-name__text'})
        if title:
            title = title.text.strip()
        if price:
            price = price.text.replace('\xa0', '')
            if int(price) < min_price:
                min_title = title
                min_price = int(price)

    return (min_price, min_title)


def make_readable(recipe: list[str]):
    readable = []
    for i in range(len(recipe)):
        stripped = recipe[i].split(',', 1)[0]
        pattern = re.compile(r'\([^(]+\)')
        result = pattern.sub('', stripped)
        result = re.sub(regex, '', result)
        result = " ".join(result.split())
        readable.append(result)

    return readable


def standardize(text: str) -> str:
    words = text.split()

    for i in range(len(words)):
        word = morph.parse(words[i])[0].normal_form
        words[i] = word

    return ' '.join(words)
