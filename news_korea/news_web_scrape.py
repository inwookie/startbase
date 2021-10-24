import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from requests.exceptions import SSLError

my_ip = 'mongodb_my_ip'
db_name = 'mongodb_db_name'
collection_name = 'mongodb_collection_name'
username = 'mongodb_username'
password = 'mongodb_password'

client = MongoClient(host=my_ip, port=27017,
                     username=username, password=password)
db = client[db_name]
collection = db[collection_name]


# 작은 갯수로 테스트
# news_items = list(collection.find(
#     {'naverNews': 'Y'}, {'_id': False}).limit(10))
# naver_news_items = list(collection.find({'naverNews': 'Y'}, {'_id': False}))
news_items = list(collection.find({}, {'_id': False}))
# print(news_items)


def scrape_image_url(url):
    image_url = 'https://image.freepik.com/free-vector/startup-construction-development-3d-thin-line-art-style-design-concept-isometric-illustration_1284-61110.jpg'

    # Request 설정값(HTTP Msg) - Desktop Chrome 인 것처럼
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    # URL request 해서 HTML 코드를 response 받음.
    try:
        data = requests.get(url, headers=headers)
    except SSLError as e:
        data = requests.get(url, headers=headers, verify=False)

    # BeautifulSoup4 사용해서 html 요소에 각각 접근하기 쉽게 만듦.
    soup = BeautifulSoup(data.text, 'html.parser')

    # image url 가져오기 - og:image
    og_img_el = soup.select_one('meta[property="og:image"]')

    if not og_img_el:
        return image_url

    image_url = og_img_el['content']

    if 'http' not in image_url:
        image_url = 'http:' + image_url

    return image_url


def scrape_content(url):
    content = ''

    # Request 설정값(HTTP Msg) - Desktop Chrome 인 것처럼
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    if 'news.naver.com' in url:
        raw_news = soup.select_one('#articeBody') or soup.select_one(
            '#articleBodyContents')
        if not raw_news:
            return content

        for tag in raw_news(['div', 'span', 'p', 'br', 'script']):
            tag.decompose()

        content = raw_news.text.strip()

    return content


for item in news_items:
    link = item['link']
    item['imageUrl'] = scrape_image_url(link)

    if item['naverNews'] == 'Y':
        content = scrape_content(link)
        # item['content'] = content
        # if content is not '':
        #     item['content'] = content
        # else:
        #     item['content'] = item['description']
        # 줄여서 쓰기
        item['content'] = content if content != '' else item['description']
        # 예. "짝수" if num % 2 == 0 else "홀수"

    else:
        item['content'] = item['description']

    # print(item)

    collection.update_one(
        {'link': link}, {'$set': {'content': item['content']}})
    collection.update_one(
        {'link': link}, {'$set': {'imageUrl': item['imageUrl']}})
