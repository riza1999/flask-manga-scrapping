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

@app.route("/api/latest")
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
    
@app.route("/api/series/<series_name>")
def series(series_name):
    link = 'https://shinigami.id/series/{}/'
    page = requests.get(link.format(series_name));

    if page.status_code == 200:
        genre_arr = []
        chapter_arr = []
        page_content = BeautifulSoup(page.content, 'html.parser')
        image_link = page_content.find(class_='summary_image').find('img').get('data-src');
        title = page_content.find(class_='post-title').find('h1').text.replace('\n','')
        synopsis = page_content.find(class_='summary__content').find('p').text
        genres = page_content.find(class_='genres-content').find_all('a')
        for genre in genres:
            genre_arr.append(genre.text)

        chapters = page_content.find_all('li',class_='wp-manga-chapter')
        for chapter in chapters:
            chapter_title = chapter.find(class_='chapter-manhwa-title').text
            chapter_release_date = chapter.find(class_='chapter-release-date').text.replace('\n','')
            chapter_arr.append({
                "title": chapter_title,
                "release_date": chapter_release_date
            })

        response = {
            "title": title,
            "image_link": image_link,
            "synopsis": synopsis,
            "genres": genre_arr,
            "chapters": chapter_arr
        }
        return response;
    else:
        return []

if __name__ == "__main__":
    app.run(debug=True)