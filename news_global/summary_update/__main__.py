# -*- coding: utf-8 -*-
import requests
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz


def main(args):
    # ========키워드 인자(argument,arg) 가져오기 ========
    db_info = args.get('DB')
    before_date = args.get('BEFORE_DATE')
    summary_api_info = args.get('SUMMARY_API')

    # ========DB 접근설정 ========
    client = MongoClient(host=db_info['my_ip'], port=27017,
                         username=db_info['username'], password=db_info['password'])
    db = client[db_info['db_name']]
    collection = db[db_info['collection_name']]

    # =====Add Date field to DB if not exist=======
    collection.update_many({'date': {'$exists': False}}, [
        {'$set': {'date': {"$toDate": "$publishedAt"}}}])

    # =====Read from Date=======
    target_date = cal_datetime_utc(before_date)

    summary_items = list(collection.find(
        {'summary': {'$exists': False}, 'date': {'$gte': target_date['date_st'], '$lte': target_date['date_end']}}, {'_id': False}))
    # print(summary_items)

    image_url = 'https://image.freepik.com/free-vector/startup-construction-development-3d-thin-line-art-style-design-concept-isometric-illustration_1284-61110.jpg'

    # =====Summary=======
    for item in summary_items:
        if 200 < len(item['content']) < 2000:
            result = item['description']
        else:
            # content -> summary field
            result = item['content']

        # DB 에 업데이트
        collection.update_one(
            {'url': item['url']}, {'$set': {'summary': result}})

    return {'process': 'end'}


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
