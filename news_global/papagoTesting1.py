import urllib.request
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz


def main(args):
    # ========키워드 인자(argument,arg) 가져오기 ========
    db_info = args.get('DB')
    before_date = args.get('BEFORE_DATE')
    trans_api_info = args.get('TRANSLATE_API')

    # ========DB 접근설정 ========
    client = MongoClient(host=db_info['my_ip'], port=27017,
                         username=db_info['username'], password=db_info['password'])
    db = client[db_info['db_name']]
    collection = db[db_info['collection_name']]

    # =====Read from Date=======
    target_date = cal_datetime_utc(before_date)

    # Find all the summary of the unicorns in a list
    trans_items = list(collection.find(
        {'summary_translated': {'$exists': False}, 'date': {'$gte': target_date['date_st'], '$lte': target_date['date_end']}}, {'_id': False}))

    for item in trans_items:
        result = translate(txt=item['summary'], client_id=trans_api_info['client_id'],
                           client_secret=trans_api_info['client_secret'])

        # DB 에 업데이트
        collection.update_one(
            {'url': item['url']}, {'$set': {'summary_translated': result}})


def translate(txt, client_id, client_secret):
    encText = urllib.parse.quote(txt)
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
        data_full = json.loads(data)
        trans_text = data_full['message']['result']['translatedText']
        print(trans_text)
        # print(response_body.decode('utf-8'))
    else:
        print("Error Code:" + rescode)

    return trans_text


def cal_datetime_utc(before_date, timezone='Asia/Seoul'):
    '''
    현재 일자에서 before_date 만큼 이전의 일자를 UTC 시간으로 변환하여 반환
    :param before_date: 이전일자
    :param timezone: 타임존
    :return: UTC 해당일의 시작시간(date_st)과 끝 시간(date_end)
    :rtype: dict of datetime object
    :Example:
    2021-09-13 KST 에 get_date(1) 실행시,
    return은 {'date_st': datetype object 형태의 '2021-09-11 15:00:00+00:00'), 'date_end': datetype object 형태의 '2021-09-12 14:59:59.999999+00:00'}
    '''
    today = pytz.timezone(timezone).localize(datetime.now())
    target_date = today - timedelta(days=before_date)

    # 같은 일자 same date 의 00:00:00 로 변경 후, UTC 시간으로 바꿈
    start = target_date.replace(hour=0, minute=0, second=0,
                                microsecond=0).astimezone(pytz.UTC)

    # 같은 일자 same date 의 23:59:59 로 변경 후, UTC 시간으로 바꿈
    end = target_date.replace(
        hour=23, minute=59, second=59, microsecond=999999).astimezone(pytz.UTC)

    return {'date_st': start, 'date_end': end}
