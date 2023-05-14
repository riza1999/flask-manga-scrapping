from flask import Flask, request
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route("/all")
def scrap():
    page = request.args.get('page', default=1);
    link = 'https://shinigami.id/semua-series/page/{}/?m_orderby=latest'.format(page);
    page = requests.get(link);

    if page.status_code == 200:
        content = []
        page_content = BeautifulSoup(page.content, 'html.parser')
        latest_card_arr = page_content.find_all(class_='page-item-detail manga')

        for i in latest_card_arr:
            title = i.find('a').get('title')
            thumbnail = i.find('img').get('data-src')
            thumbnail_set = i.find('img').get('data-srcset')
            content_type = i.find('span').text
            score = i.find(class_='score').text
            latest_chapter = []
            temp = i.find_all(class_='chapter-item')
            for x in temp:
                chapter_title = x.find('a', class_='btn-link').text.lstrip()
                chapter_post_on = x.find('span', class_='post-on').text.replace('\n','')
                latest_chapter.append({"chapter_title":chapter_title, "chapter_post_on":chapter_post_on})

            response = {
                "title": title,
                "thumbnail": thumbnail,
                "thumbnail_set": thumbnail_set,
                "content_type" : content_type,
                "score" : score,
                "latest_chapter" : latest_chapter
            }

            content.append(response);
        return content;
    else:
        return []