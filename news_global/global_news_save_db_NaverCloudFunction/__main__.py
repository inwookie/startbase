import requests
import json
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from datetime import date, timedelta


def main(args):
    host = args.get('host')
    username = args.get('username')
    password = args.get('password')
    db_name = args.get('db_name')
    collection_name = args.get('collection_name')

    # =====Global News 정보 가져오기=====
    docs = global_news()

    # ====News 를 DB 에 저장====
    result = save_to_db(host, username, password,
                        db_name, collection_name, docs)

    return result


def global_news():
    # ====================News API============================
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

    # 뉴스 link field 에 unique key 설정 - unique 하게 유일한 row 데이터만 입력됨.
    collection.create_index([('title', 1)], unique=True)

    # summary_items = list(collection.find({}, {'_id': False}))
    # for item in summary_items:
    #     if 200 < len(item['content']) < 2000:
    #         result = item['content']
    #     else:
    #         # description -> summary field
    #         result = item['description']
    #     # DB 에 업데이트
    #     collection.update_one(
    #         {'link': item['link']}, {'$set': {'summary': result}})

    try:
        collection.insert_many(docs, ordered=False)

    except BulkWriteError as bwe:
        db_result['result'] = 'Insert and Ignore duplicated data'

    return db_result
