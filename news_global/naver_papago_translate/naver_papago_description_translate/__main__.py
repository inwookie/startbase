import urllib.request
import json
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from datetime import date, timedelta
import pytz


def main(args):
    # ========키워드 인자(argument,arg) 가져오기 ========
    db_info = args.get('DB')
    before_date = args.get('BEFORE_DATE')

    # ========DB 접근설정 ========
    client = MongoClient(host=db_info['my_ip'], port=27017,
                         username=db_info['username'], password=db_info['password'])
    db = client[db_info['db_name']]
    collection = db[db_info['collection_name']]

    target_date = cal_datetime_utc(before_date)

    summary_translated_items = list(collection.find(
        {'summary_translated': {'$exists': False}, 'date': {'$gte': target_date['date_st'], '$lte': target_date['date_end']}}, {'_id': False}))

    def papago_translate():
        total_trans_text = []
        client_id = "client_id"
        client_secret = "client_secret"
        for item in summary_translated_items:
            encText = urllib.parse.quote(item['summary'])
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
                    {'trans_description': trans_text, 'publishedAt': date})
            else:
                print("Error Code:" + rescode)

        trans_date = [dict['publishedAt']
                      for dict in total_trans_text]
        trans_text = [dict['trans_description']
                      for dict in total_trans_text]

        db_result = {'result': 'success'}
        try:
            for date, translated in zip(trans_date, trans_text):
                collection.update_one(
                    {'publishedAt': date}, {'$set': {'description_translated': translated}})
        except BulkWriteError as bwe:
            db_result['result'] = 'Insert and Ignore duplicated data'
        return db_result
    final = papago_translate()
    print(final)
    return final


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
