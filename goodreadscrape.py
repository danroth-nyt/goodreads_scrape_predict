import time
import re
import pickle
import random
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


def search_gr(ref_nums):
    """Generate dataframe of Goodreads book information"""
    driver = webdriver.Chrome('/home/danroth/chromedriver')
    # driver.set_window_position(-2000,0)  # this function will minimize the window
    ref_nums = ref_nums
    book_nums = []
    titles = []
    authors = []
    dates = []
    ratings = []
    genres = []
    formats = []
    page_num = []
    langs = []
    num_likes = []
    print('Searching books')
    for i, book_reference_number in enumerate(ref_nums):
        print(i, book_reference_number)
        driver.get("https://www.goodreads.com/book/show/"+str(book_reference_number))
        soup = BeautifulSoup(driver.page_source, 'lxml')
        try:
            book_title = soup.select('.gr-h1.gr-h1--serif')[0].text.strip()
        except:
            book_title = ''
        try:
            author_name = soup.select('.authorName')[0].text.strip()
        except:
            author_name = ''
        try:
            rating = soup.find("span", itemprop="ratingValue").text.strip()
        except:
            rating = ''
        try:
            genre = soup.findAll("div", {"class": "elementList"})[0].a.get_text()
        except:
            genre = ''
        try:
            format = soup.find("span", itemprop="bookFormat").text.strip()
        except:
            format = ''
        try:
            pages = soup.find("span", itemprop="numberOfPages").text.strip(' pages')
        except:
            pages = ''
        try:
            date_string = soup.findAll("div", {"class": "row"})[1].get_text()
            date = re.search(r"(\w+\s)(\w+\s\d+$|\d+$)", date_string, re.MULTILINE).group(0)
        except:
            date = ''
        try:
            lang = soup.find("div", itemprop="inLanguage").text
        except:
            lang = ''
        try:
            rating_more = driver.find_element_by_xpath("//a[@id, 'rating_details']")
            rating_more.click()
            likes = soup.find("span", {"class": "value"})
        except:
            likes = ''
        book_nums.append(book_reference_number)
        titles.append(book_title)
        authors.append(author_name)
        dates.append(date)
        ratings.append(rating)
        genres.append(genre)
        formats.append(format)
        page_num.append(pages)
        langs.append(lang)
        num_likes.append(likes)
        d = {'book_num': book_nums, 'title': titles, 'author': authors, 'publish_date': dates, 'rating': ratings,
             'genre': genres, 'format': formats, 'pages': page_num, 'language': langs, 'likes': num_likes}
        book_df = pd.DataFrame(d)
        # if i + 1 % 150 == 0:
        #     time.sleep(320)
        time.sleep(2)
    driver.close()
    print('Initial book scrape complete')
    return book_df


def gr_stats(ref_nums):
    """Generate dataframe of Goodreads book statistics"""
    stats_driver = webdriver.Chrome('/home/danroth/chromedriver')  # create driver
    first_number = ref_nums[0]
    stats_driver.get("https://www.goodreads.com/book/stats?id=" + str(first_number))

    login = stats_driver.find_element_by_xpath('//a[contains(@href, "/user/sign_in")]')  # perform login
    login.click()
    username = stats_driver.find_element_by_xpath("//input[@id='user_email']")
    username.send_keys("d.roth1@unimail.derby.ac.uk")
    password = stats_driver.find_element_by_xpath("//input[@id='user_password']")
    password.send_keys("metispass6.")
    sign_in = stats_driver.find_element_by_xpath("//input[@class='gr-button gr-button--large']")
    sign_in.click()

    l = []
    print('Start scrape book stats')
    for i, book_reference_number in enumerate(ref_nums):
        print(i, book_reference_number)
        # if i + 1 % 150 == 0:
        #     time.sleep(320)
        time.sleep(2)
        stats_driver.get("https://www.goodreads.com/book/stats?id=" + str(book_reference_number))
        try:
            show_table = stats_driver.find_element_by_xpath("//a[contains(@class, 'smallText')]")
            show_table.click()
            stats_soup = BeautifulSoup(stats_driver.page_source, 'lxml')
            table = stats_soup.find('div', id='dataTable')  # find and process table
            table_rows = table.find_all('tr')
            for tr in table_rows:
                td = tr.find_all('td')
                row = [tr.text for tr in td]
                row.append(book_reference_number)
                l.append(row)
        except:
            continue

    cols = ['date', 'added', 'ratings', 'reviews', 'to_read', 'book_num']
    bookstats_df = pd.DataFrame(l, columns=cols)
    bookstats_df.dropna(inplace=True)
    bookstats_df = bookstats_df.reset_index().drop('index', axis=1)
    bookstats_df.book_num = bookstats_df.book_num.apply(lambda x: int(x))
    bookstats_df['to_read'] = bookstats_df['to_read'].apply(lambda x: int(x))
    books_toread = bookstats_df.groupby('book_num').agg({'to_read': 'mean'}).reset_index()
    stats_driver.close()
    print('Stats scrape complete')
    return books_toread


def process_gr(ref_nums):
    book_df = search_gr(ref_nums)
    stats_df = gr_stats(ref_nums)
    final_df = pd.merge(book_df, stats_df, left_on='book_num', right_on='book_num')
    return final_df


def main():
    """Essential variables"""
    api_key = 'jpzuzysfQRRMex0Ovlmpg'
    num_samples = 10
    random.seed(115)
    book_nums = random.sample(range(1, 8630000), num_samples)  # Last book is 8,630,000

    """Process and save dataframe"""
    # book_df_raw = process_gr(book_nums)
    # book_df_raw = book_df_raw.replace('', np.nan)
    # with open('./data/book_data.pkl', 'wb') as savefile:
    #     pickle.dump(book_df_raw, savefile)

    """Open and manipulate dataframe"""
    # with open("./data/book_data.pkl", 'rb') as openfile:
    #     book_df = pickle.load(openfile)
    # print(book_df.head(), book_df.tail())

    """Test"""
    # driver = webdriver.Chrome('/home/danroth/chromedriver')
    # driver.get("https://www.goodreads.com/book/show/" + str(1000))
    # rating_more = driver.find_element_by_xpath("//a[@id, 'rating_details']")
    # rating_more.click()
    # soup = BeautifulSoup(driver.page_source, 'lxml')
    book_df = search_gr([1000])
    print(book_df.likes)


if __name__ == "__main__":
    main()
