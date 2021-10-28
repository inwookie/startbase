# StartBase - Startup Audio News

<div id="top"></div>

![](https://github.com/inwookie/startbase/blob/main/preview/home.png?raw=true)

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

https://kr.object.ncloudstorage.com/startbase-news/2021-10-26_korean.mp3/2021-10-26_21.mp3

https://kr.object.ncloudstorage.com/startbase-news/2021-10-26_global.mp3/2021-10-26_6.mp3

<!-- ABOUT THE PROJECT -->

## About The Project

StartBase is for those who would love to read more news about startups, or even better, listen to summarized news and save their time during a busy day. This is my first full-stack web service project, which was inspired by my desire to read more news about startups and, if possible, to listen to them while I prepare for my breakfast. This project is for those who would love to:

- Get daily curated Korean news about startups and listen to a summarized version of the curated news.

- Get daily curated global news about startups and llisten to a translated and summarized version of that curated news.

### Built With

- [Naver Cloud](https://www.ncloud.com/product/compute/server)
- [Naver Cloud Function](https://www.ncloud.com/product/compute/cloudFunctions)
- [Naver Cloud Object Storage](https://www.ncloud.com/product/storage/objectStorage)
- [Naver Cloud AI Service](https://www.ncloud.com/product/aiService)
- [MongoDB](https://www.mongodb.com/)
- [Bootstrap](https://getbootstrap.com)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)

### The Architecture

![](https://github.com/inwookie/startbase/blob/main/preview/architecture.png?raw=true)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- Implemented Features -->

## Implemented Features

### Get News

Naver News API and News API were used to get the daily news about startups. During the process, if the given data does not include an url image or contents, those information will be scraped from the relevant website. Once the process has been completed, it will be saved in the MongoDB collection. This process would be repeated multiple times during the day by Naver Cloud Function.

```python
# Accessing Naver News API
    for keyword in keywords:
        url = 'https://openapi.naver.com/v1/search/news.json'
        sort = 'date'
        start_num = 1

        params = {'display': display_num, 'start': start_num,
                  'query': keyword.encode('utf-8'), 'sort': sort}
        headers = {'X-Naver-Client-Id': client_id,
                   'X-Naver-Client-Secret': client_secret, }

        r = requests.get(url, headers=headers,  params=params)

        if r.status_code == requests.codes.ok:
            result_response = json.loads(r.content.decode('utf-8'))
```

```python
# Web Scrape - Image
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    try:
        data = requests.get(url, headers=headers)
    except SSLError as e:
        data = requests.get(url, headers=headers, verify=False)

    soup = BeautifulSoup(data.text, 'html.parser')

    og_img_el = soup.select_one('meta[property="og:image"]')

    if not og_img_el:
        return image_url

    image_url = og_img_el['content']

    if 'http' not in image_url:
        image_url = 'http:' + image_url
```

```python
# Save to DB
    client = MongoClient(host=my_ip, port=27017,
                         username=username, password=password)
    db = client[db_name]
    collection = db[collection_name]

    collection.create_index([('link', 1)], unique=True)

    try:
        collection.insert_many(docs, ordered=False)

    except BulkWriteError as bwe:
        db_result['result'] = 'Insert and Ignore duplicated data'
```

_For the full code, please refer to the  [Naver News API](https://github.com/inwookie/startbase/blob/main/news_korea/naver_news_save_db_NaverCloudFunction/__main__.py) & [News API](https://github.com/inwookie/startbase/blob/main/news_global/global_news_save_db_NaverCloudFunction/__main__.py)_

### Summarize

Accumulated news needs to be summarized because the Voice API limits its maximum characters to 1000 per call. Summary API would use the content of the news and return it in two sentences. Using the option of the API, the tone of the summarized text would not be changed from the original.

```python
# Accessing Naver Summary API
    headers = {'X-NCP-APIGW-API-KEY-ID': client_id,
               'X-NCP-APIGW-API-KEY': client_secret,
               'Content-Type': 'application/json'}

    document = {'content': txt}
    option = {'language': 'ko', 'model': 'news', 'tone': 0, 'summaryCount': 2}

    data = {'document': document, 'option': option}

    r = requests.post('https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize',
                      headers=headers, data=json.dumps(data))

    summary_txt = ''
    if r.status_code == requests.codes.ok:
        result_response = json.loads(r.content)
        summary_txt = result_response['summary']
```

_For the full code, please refer to the  [Naver Summary API](https://github.com/inwookie/startbase/blob/main/news_korea/naver_news_summary_update_NaverCloudFunction/__main__.py)_

### Translate

Accumulated English news needs to be translated in order to be used for the Voice API as Naver Voice API only supports Korean and Japanese text as of right now.

```python
# Accessing Naver Papago API
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
```

_For the full code, please refer to the  [Naver Papago API](https://github.com/inwookie/startbase/blob/main/news_global/naver_papago_translate/naver_papago_summary_translate/__main__.py)_

### Voice

The summarized and translated contents of the news will be converted to an audio file using the Naver Voice API. Because the character limit is 1000 characters, four summary data would be combined and converted to an audio file and be saved to object storage. To save space, audio files would be deleted once they have been stored in object storage.

```python
# Accessing Naver Summary API
    headers = {'X-NCP-APIGW-API-KEY-ID': client_id,
               'X-NCP-APIGW-API-KEY': client_secret,
               'Content-Type': 'application/json'}

    document = {'content': txt}
    option = {'language': 'ko', 'model': 'news', 'tone': 0, 'summaryCount': 2}

    data = {'document': document, 'option': option}

    r = requests.post('https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize',
                      headers=headers, data=json.dumps(data))

    summary_txt = ''
    if r.status_code == requests.codes.ok:
        result_response = json.loads(r.content)
        summary_txt = result_response['summary']
```

```python
    date_cnt_items = collection.count_documents({
        'date': {'$gte': target_date['date_st'], '$lte': target_date['date_end']}})

    # Combine four summary data per api call
    page_num = (date_cnt_items // 4) + (0 if date_cnt_items % 4 == 0 else 1)

    for i in range(page_num):
        file_name = f'{kst_target_date}_{i+1}.mp3'

        skip_num = i * 4

        limit_items = list(collection.find(
            {'date': {'$gte': target_date['date_st'], '$lte': target_date['date_end']}}, {'_id': False}).sort('date', 1).skip(skip_num).limit(4))

        summary_contents = ''

        for item in limit_items:
            summary_contents = (f'다음 뉴스.  '.join(
                item['summary'] for item in limit_items))[: 999]

        # =========Voice Convert=========
        print(f'======{len(summary_contents)}======')

        result = tts(client_id=voice_storage_info['client_id'], client_secret=voice_storage_info['client_secret'],
                     text=summary_contents, file_folder=file_folder, file_name=file_name)

        # =========Upload to Object Storage =========
        local_info['local_file'] = file_name
        bucket_info['upload_file'] = file_name
        bucket_info['upload_folder'] = f'{kst_target_date}_korean.mp3'

        if result['status'] == 'ok':
            upload_storage(storage_info=storage_info, local_info=local_info,
                           bucket_info=bucket_info)
            # Delete the file once it has been saved to Object Storage
            result_msg = remove_file(
                local_info['local_folder'], local_info['local_file'])
            print(result_msg)
```

```python
    # Upload to Object Storage
    service_name = 's3'
    endpoint_url = 'https://kr.object.ncloudstorage.com'
    region_name = 'kr-standard'

    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=storage_info['access_key'],
                      aws_secret_access_key=storage_info['secret_key'])

    dir_parts = [local_info['local_file']]
    local_path = str(Path.cwd().joinpath(*dir_parts))
    print(f'upload_storage : {local_path}')

    upload_path = f'{bucket_info["upload_folder"]}/{bucket_info["upload_file"]}'

    s3.upload_file(local_path, bucket_info['bucket_name'], upload_path,
                   ExtraArgs={'ACL': 'public-read'})
```

```python
    # Delete a file after upload has been completed
    dir_parts = [file_folder, file_name]
    path = Path.cwd().joinpath(*dir_parts)

    try:
        if os.path.isfile(path):
            os.remove(path)
            result = f'{path} 파일이 삭제되었습니다.'
        else:
            result = f'Error: {path} 를 찾을 수 없습니다.'
    except OSError as e:
        result = f'Error: {e.filename} - {e.strerror}.'
```

_For the full code, please refer to the  [Naver Voice API](https://github.com/inwookie/startbase/blob/main/voice_api/voice_korea_source/__main__.py)_

### Convert to UTC

Because MongoDB is wired in UTC, date and time needs to be converted to UTC from current timezone of Asia/Seoul.

```python
def cal_datetime_utc(before_date, timezone='Asia/Seoul'):

    today = pytz.timezone(timezone).localize(datetime.now())
    target_date = today - timedelta(days=before_date)

    start = target_date.replace(hour=0, minute=0, second=0,
                                microsecond=0).astimezone(pytz.UTC)

    end = target_date.replace(
        hour=23, minute=59, second=59, microsecond=999999).astimezone(pytz.UTC)

    return {'date_st': start, 'date_end': end}
```

### Mongo DB

<div>
<img width="500" alt="온보딩2" src="https://github.com/inwookie/startbase/blob/main/preview/mongodb1.png?raw=true">
</div>

![](https://github.com/inwookie/startbase/blob/main/preview/mongodb1.png?raw=true)
![](https://github.com/inwookie/startbase/blob/main/preview/mongodb2.png?raw=true)

### Object Storage

![](https://github.com/inwookie/startbase/blob/main/preview/home.png?raw=true)
![](https://github.com/inwookie/startbase/blob/main/preview/home.png?raw=true)

<!-- ROADMAP -->

## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [] Add Additional Templates w/ Examples
- [] Add "components" document to easily copy & paste sections of the readme
- [] Multi-language Support
  - [] Chinese
  - [] Spanish

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

- [Choose an Open Source License](https://choosealicense.com)
- [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
- [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
- [Malven's Grid Cheatsheet](https://grid.malven.co/)
- [Img Shields](https://shields.io)
- [GitHub Pages](https://pages.github.com)
- [Font Awesome](https://fontawesome.com)
- [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
