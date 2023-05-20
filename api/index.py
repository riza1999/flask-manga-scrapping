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
                chapter_title = x.find('a', class_='btn-link').text.lstrip().rstrip()
                chapter_post_on = x.find('span', class_='post-on').text.replace('\n','')
                latest_chapter.append({"title":chapter_title, "post_on":chapter_post_on})

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
        title = page_content.find(class_='post-title').find('h1').text.replace('\n','').lstrip().rstrip()
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

@app.route("/api/series/<series_name>/<chapter>")
def chapter(series_name,chapter):
    link = 'https://shinigami.id/series/{}/{}/'
    page = requests.get(link.format(series_name,chapter))
    if page.status_code == 200:
        img_arr = [];
        chapter_arr = [];
        page_content = BeautifulSoup(page.content, 'html.parser')
        reading_content = page_content.find(class_='reading-content').find_all('img');
        for x in reading_content:
            link = x.get('data-src').replace('\t','').replace('\n','');
            img_arr.append(link);

        chapters = page_content.find(class_='single-chapter-select').find_all('option')
        for chapter in chapters:
            title = chapter.text.replace('\n','').lstrip().rstrip();
            isSelected = chapter.get('selected') is not None;
            chapter_arr.append({'title': title,'isSelected':isSelected});
        
        title = page_content.find(class_='breadcrumb').find_all('li')[2].text.replace('\n','').lstrip().rstrip()

        response = {
            'chapters': chapter_arr,
            'image_content': img_arr,
            'title': title
        }

        return response;
    else:
        return []

@app.route("/api/search")
def search():
    currPage = request.args.get('page', default=1);
    tSearch = request.args.get('tSearch', default='');
    link = 'https://shinigami.id/page/{}/?s={}&post_type=wp-manga'.format(currPage,tSearch)
    page = requests.get(link)

    if page.status_code == 200:
        searchs = [];
        page_content = BeautifulSoup(page.content, 'html.parser')
        search_content = page_content.find(class_='tab-content-wrap').find_all(class_='row c-tabs-item__content') if page_content.find(class_='tab-content-wrap') is not None else None;

        if search_content is not None:
            total_search = page_content.find(class_='c-blog__heading style-2 font-heading').find('h1').text.replace('\n','').strip()
            current_page = page_content.find(class_='current').text if page_content.find(class_='current') is not None else '1'
            prev_page = page_content.find(class_='previouspostslink') is not None
            next_page = page_content.find(class_='nextpostslink') is not None

            for x in search_content:
                img = x.find('img').get('data-src');
                title = x.find(class_='post-title').text.lstrip().rstrip();
                genres =  x.find(class_='post-content_item mg_genres').find(class_='summary-content').find_all('a')
                genres_arr = [genre.text for genre in genres]
                latest_chapter = x.find(class_='font-meta chapter').text.lstrip().rstrip();
                latest_chapter_link = x.find(class_='font-meta chapter').find('a').get('href');
                latest_chapter_post_on = x.find(class_='meta-item post-on').text.lstrip().rstrip();

                searchs.append({
                    "thumbnail": img,
                    "title": title,
                    "genres": genres_arr,
                    "latest_chapter": [{
                        "title": latest_chapter,
                        "link": latest_chapter_link,
                        "post_on": latest_chapter_post_on
                    }]
                })

            response = {
                'total_search': total_search,
                'current_page': current_page,
                'prev_page': prev_page,
                'next_page': next_page,
                'searchs': searchs
            }
        else:
            response = {
                'total_search': 0,
                'current_page': 1,
                'prev_page': False,
                'next_page': False,
                'searchs': []
            }
        return response
    else:
        return []

if __name__ == "__main__":
    app.run(debug=True)