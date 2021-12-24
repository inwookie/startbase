# 🚀 StartBase - Startup Audio News

<div id="top"></div>

![](https://github.com/inwookie/startbase/blob/main/preview/img/home.png?raw=true)

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#the-architecture">The Architecture</a></li>
      </ul>
    </li>
    <li>
      <a href="#implemented-features">Implemented Features</a>
      <ul>
        <li><a href="#get-news">Get News</a></li>
        <li><a href="#summarize">Summarize</a></li>
        <li><a href="#summarize">Summarize</a></li>
        <li><a href="#translate">Translate</a></li>
        <li><a href="#voice">Voice</a></li>
        <li><a href="#convert-to-utc">Convert to UTC</a></li>
        <li><a href="#mongo-db">Mongo DB</a></li>
        <li><a href="#object-storage">Object Storage</a></li>
        <li><a href="#card-news">Card News</a></li>
        <li><a href="#calamansi-audio-player">Calamansi Audio Player</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#demo">Demo</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

StartBase is for those who would love to read more news about startups, or even better, listen to summarized news and save their time during a busy day. This is my first full-stack web service project, which was inspired by my desire to read more news about startups and, if possible, to listen to them while I prepare for my breakfast. This project is for those who would love to:

- Get daily curated Korean news about startups and listen to a summarized version of the curated news.

- Get daily curated global news about startups and llisten to a translated and summarized version of that curated news.

> **Project Duration** : 2021.10.04 ~ 2021.10.28

### Built With

- [Naver Cloud](https://www.ncloud.com/product/compute/server)
- [Naver Cloud Function](https://www.ncloud.com/product/compute/cloudFunctions)
- [Naver Cloud Object Storage](https://www.ncloud.com/product/storage/objectStorage)
- [Naver Cloud AI Service](https://www.ncloud.com/product/aiService)
- [MongoDB](https://www.mongodb.com/)
- [Bootstrap](https://getbootstrap.com)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)

### The Architecture

![](https://github.com/inwookie/startbase/blob/main/preview/img/architecture.png?raw=true)

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

![](https://github.com/inwookie/startbase/blob/main/preview/img/mongodb1.png?raw=true)
![](https://github.com/inwookie/startbase/blob/main/preview/img/mongodb2.png?raw=true)

### Object Storage

<div>
<img width="197" alt="온보딩2" src="https://github.com/inwookie/startbase/blob/main/preview/img/object_storage1.png?raw=true">
<img width="600" alt="온보딩2" src="https://github.com/inwookie/startbase/blob/main/preview/img/object_storage2.png?raw=true">
</div>

### Card News

Implement card news on a webpage using javascript.

```javascript
const url = "/api/news";
// Get news data from API
fetch(url, init)
  .then((res) => {
    if (res.status === 200) {
      return res.json();
    } else {
      console.error(`HTTP error! status: ${res.status}`);
    }
  })
  .then((jsonData) => {
    for (let i = 0; i < jsonData["news"].length; i++) {
      const item = jsonData["news"][i];
      let description = item["description"];
      let link = item["link"];
      let imageUrl = item["imageUrl"];

      let card = `<div class="col">
                                    <div class="card shadow-sm">
                                        <img src="${imageUrl}"
                                            class="card-img-top" alt="...">
                                        <div class="card-body">
                                            <p class="card-text">${description}
                                            </p>
                                            <div class="d-flex justify-content-between align-items-center">
                                                <div class="btn-group">
                                                    <a href="${link}"
                                                        type="button" class="btn btn-sm btn-outline-secondary">View</a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>`;

      let comments = document.getElementById("news");
      comments.insertAdjacentHTML("beforeend", card);
    }
  })
  .catch((err) => {
    console.log(err);
  });
```

### Calamansi Audio Player

Gain audio file from Object Storage and display it through [Calamansi Audio Player](https://github.com/voerro/calamansi-js).

```javascript
// Get audio file from Object Storage
const audio_url = "/api/audios";
fetch(audio_url, init)
  .then((res) => {
    if (res.status === 200) {
      return res.json();
    } else {
      console.error(`HTTP error! status: ${res.status}`);
    }
  })
  .then((jsonData) => {
    new Calamansi(document.querySelector("#calamansi-player-1"), {
      skin: "https://kr.object.ncloudstorage.com/startbase-news/asset/skins",
      playlists: {
        News: jsonData["audio_list"],
      },
      defaultAlbumCover:
        "https://kr.object.ncloudstorage.com/startbase-news/asset/skins/default-album-cover.png",
    });
  })
  .catch((err) => {
    console.log(err);
  });
```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

**Backend**

- [x] Create Server - Naver Cloud
- [x] Get Korean News - Naver News API
  - [x] Web Scrape
    - [x] URL Image
    - [x] Content
  - [x] Save to DB - MongoDB
  - [x] Implement it to Naver Cloud Function
- [x] Summarize - Naver Summary API
  - [x] Save to DB - MongoDB
  - [x] Implement it to Naver Cloud Function
- [x] Get Datetime - Convert to UTC
- [x] Get Global News - News API
  - [x] Save to DB - MongoDB
  - [x] Implement it to Naver Cloud Function
- [x] Translate Global News - Papago API
  - [x] Save to DB - MongoDB
  - [x] Implement it to Naver Cloud Function
- [x] Create Object Storage
- [x] Voice - Naver Voice API
  - [x] Save to Object Storage
  - [x] Implement it to Naver Cloud Function

**Frontend**

- [x] Create Flask Web App
  - [x] Get news data from DB
  - [x] Get audio files from Object Storage
  - [x] Implement Bootstrap v5.0
  - [x] Design web page using HTML/CSS/Javascript

**Release**

- [x] Get/Buy Domain
- [x] Configure NCP Object Storage
  - [x] Ncloud CLI
  - [x] AWS CLI
- [x] Upload to server using FileZilla
- [x] Configure virtual environment
  - [x] Execute in background

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- Demo -->

## Demo

### Audio File

Example Audio File 1 [Listen](https://kr.object.ncloudstorage.com/startbase-news/2021-10-26_korean.mp3/2021-10-26_21.mp3)

Example Audio File 2 [Listen](https://kr.object.ncloudstorage.com/startbase-news/2021-10-26_global.mp3/2021-10-26_6.mp3)

### Home

![](https://github.com/inwookie/startbase/blob/main/preview/gif/home.gif?raw=true)

### Audio

![](https://github.com/inwookie/startbase/blob/main/preview/img/audio.png?raw=true)

</br>

![](https://github.com/inwookie/startbase/blob/main/preview/gif/audio.gif?raw=true)

### News - Korea

![](https://github.com/inwookie/startbase/blob/main/preview/img/news_korea.png?raw=true)

</br>

![](https://github.com/inwookie/startbase/blob/main/preview/gif/news_korea.gif?raw=true)

### News - Global

![](https://github.com/inwookie/startbase/blob/main/preview/img/news_global.png?raw=true)

</br>

![](https://github.com/inwookie/startbase/blob/main/preview/gif/news_global.gif?raw=true)

### Contact

![](https://github.com/inwookie/startbase/blob/main/preview/img/contact.png?raw=true)

### Navigation

![](https://github.com/inwookie/startbase/blob/main/preview/gif/nav.gif?raw=true)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

### Inwook Baek

**Email:** inwook.baek@gmail.com

**Notion:** [Link](https://www.notion.so/inwook/Inwook-Baek-4778a344f4b84a42b2c6ef799d62f54b)

**LinkedIn:** [Link](https://www.linkedin.com/in/inwook-baek/)

<p align="right">(<a href="#top">back to top</a>)</p>
