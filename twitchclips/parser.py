import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def get_clip_link(link):
    try:
        url = link
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        time.sleep(3)
        page = driver.page_source
        driver.quit()
        soup = BeautifulSoup(page, 'html.parser')
        videos = soup.find_all('video')

        for video in videos:
            src = video['src']
            if src:
                return src
            else:
                return False
    except:
        return False
