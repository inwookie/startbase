import requests
import json
from datetime import date, timedelta
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

# =======DB 저장 TEST==========
host = 'mongodb_host'
username = 'mongodb_username'
password = 'mongodb_password'

db_name = 'mongodb_db_name'
collection_name = 'mongodb_collection_name'


YESTERDAY = date.today() - timedelta(1)
API_KEY = "API_KEY"
url = "https://newsapi.org/v2/everything"

querystring = {
    "qInTitle": "startup",
    "language": "en",
    "pageSize": "100",
    "from": YESTERDAY,
    "sortBy": "popularity"
}

headers = {
    'X-Api-Key': API_KEY
}

r = requests.request("GET", url, headers=headers, params=querystring)


def get_global_news():
    total_articles = []
    if r.status_code == requests.codes.ok:
        result_response = json.loads(r.content.decode('utf-8'))
        result_response_article = result_response['articles']

        for item in result_response_article:
            article = {
                'source': item['source']['name'],
                'author': item['author'],
                'title': item['title'],
                'description': item['description'],
                'url': item['url'],
                'urlToImage': item['urlToImage'],
                'publishedAt': item['publishedAt'],
                'content': item['content']
            }
            total_articles.append(article)
    else:
        print('request failed')
        failed_msg = json.loads(r.content.decode('utf-8'))
        print(failed_msg)
    return total_articles


def save_to_db(my_ip, username, password, db_name, collection_name, docs):
    """
    딕셔너리 리스트를 데이터베이스에 저장
    :params str my_ip: 데이터베이스 IP
    :params str username: 데이터베이스 계정
    :params str password: 데이터베이스 계정 비밀번호
    :params str db_name: 데이터베이스 이름
    :params str collection_name: 데이터베이스 collection 이름
    :params list docs: 데이터베이스 저장할 딕셔너리 리스트
    :return result: 데이터베이스 저장 결과
    :rtype dict
    """
    db_result = {'result': 'success'}

    client = MongoClient(host=my_ip, port=27017,
                         username=username, password=password)
    db = client[db_name]
    collection = db[collection_name]  # unique key 설정할 collection

    # 뉴스 title field 에 unique key 설정 - unique 하게 유일한 row 데이터만 입력됨.
    collection.create_index([('title', 1)], unique=True)

    try:
        collection.insert_many(docs, ordered=False)

    except BulkWriteError as bwe:
        db_result['result'] = 'Insert and Ignore duplicated data'

    return db_result


docs = get_global_news()
result = save_to_db(host, username, password, db_name, collection_name, docs)
