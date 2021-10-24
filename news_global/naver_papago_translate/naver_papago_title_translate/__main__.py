import urllib.request
import json
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from datetime import date, timedelta


def main(args):
    host = args.get('host')
    username = args.get('username')
    password = args.get('password')
    db_name = args.get('db_name')

    YESTERDAY = date.today() - timedelta(1)
    YESTERDAY = f"{str(YESTERDAY)}T00:00:00Z"

    client = MongoClient(host=host, port=27017,
                         username=username, password=password)
    access_db = client.db_name
    access_db_collection = access_db.news_api_top

    # Turn all the data from yesterday from a collection into a list
    article_list_time_adjusted = list(access_db_collection.find(
        {'publishedAt': {'$gt': YESTERDAY}}))

    # Find all the titles of the global news in a list
    article_title = [dict['title']
                     for dict in article_list_time_adjusted]

    article_publishedAt = [dict['publishedAt']
                           for dict in article_list_time_adjusted]

    def papago_translate():
        total_trans_text = []
        client_id = "client_id"
        client_secret = "client_secret"
        for title, date in zip(article_title, article_publishedAt):
            encText = urllib.parse.quote(title)
            data = "source=en&target=ko&text=" + encText
            url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
            request = urllib.request.Request(url)
            request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
            request.add_header("X-NCP-APIGW-API-KEY", client_secret)
            response = urllib.request.urlopen(
                request, data=data.encode("utf-8"))
            rescode = response.getcode()
            if(rescode == 200):
                response_body = response.read()
                data = response_body.decode('utf-8')
                data_full = json.loads(data)
                # print(data_full)
                trans_text = data_full['message']['result']['translatedText']
                total_trans_text.append(
                    {'trans_title': trans_text, 'publishedAt': date})
            else:
                print("Error Code:" + rescode)

        trans_date = [dict['publishedAt']
                      for dict in total_trans_text]
        trans_text = [dict['trans_title']
                      for dict in total_trans_text]

        db_result = {'result': 'success'}
        try:
            for date, translated in zip(trans_date, trans_text):
                access_db_collection.update_one(
                    {'publishedAt': date}, {'$set': {'title_translated': translated}})
        except BulkWriteError as bwe:
            db_result['result'] = 'Insert and Ignore duplicated data'
        return db_result
    final = papago_translate()
    # print(final)
    return final
