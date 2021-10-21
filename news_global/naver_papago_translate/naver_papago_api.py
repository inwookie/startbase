# 네이버 Papago NMT API
import urllib.request
import json
from pymongo import MongoClient
from datetime import date, timedelta

# =======DB 저장 TEST==========
host = '___________'
username = '___________'
password = '___________'

db_name = '___________'
collection_name = '___________'

YESTERDAY = date.today() - timedelta(1)
YESTERDAY = f"{str(YESTERDAY)}T00:00:00Z"

client = MongoClient(host=host, port=27017,
                     username=username, password=password)
access_db = client.likelion
access_db_collection = access_db.news_api_top

# Turn all the data from yesterday from a collection into a list
article_list_time_adjusted = list(access_db_collection.find(
    {'publishedAt': {'$gt': YESTERDAY}}))

# Find all the descriptions of the news in a list
article_description = [dict['description']
                       for dict in article_list_time_adjusted]


def papago_translate():
    total_trans_text = []
    client_id = "___________"
    client_secret = "___________"
    for description in article_description:
        encText = urllib.parse.quote(description)
        data = "source=en&target=ko&text=" + encText
        url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
        request = urllib.request.Request(url)
        request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
        request.add_header("X-NCP-APIGW-API-KEY", client_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()
        if(rescode == 200):
            response_body = response.read()
            data = response_body.decode('utf-8')
            data = json.loads(data)
            trans_text = data['message']['result']['translatedText']
            total_trans_text.append(trans_text)
        else:
            print("Error Code:" + rescode)
    print(total_trans_text)
    return total_trans_text


papago_translate()
