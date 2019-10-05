import time
import re
import pickle
import random
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
pd.set_option('display.expand_frame_repr', False)  # display full dataframe width


def search_gr(ref_nums):
    """Generate dataframe of Goodreads book information"""
    driver = webdriver.Chrome('/home/danroth/chromedriver')
    ref_nums = ref_nums
    book_nums, titles, authors, followers, dates, og_dates, ratings, genres, bindings, page_num, lang,\
        num_likes, trivia_qs, quote_likes, rev_likes, num_ratings, num_revs = ([] for i in range(17))
    print('Searching books')
    for i, book_reference_number in enumerate(ref_nums):
        print(i, book_reference_number)
        driver.get("https://www.goodreads.com/book/show/"+str(book_reference_number))
        soup = BeautifulSoup(driver.page_source, 'lxml')
        book_nums.append(book_reference_number)
        try:
            titles.append(soup.select('.gr-h1.gr-h1--serif')[0].text.strip())
        except:
            titles.append('Unknown')
        try:
            authors.append(soup.select('.authorName')[0].text.strip())
        except:
            authors.append('Unknown')
        try:
            follower_str = soup.find("div", {"class": "bookAuthorProfile__followerCount"}).get_text()
            followers.append(int(''.join(re.findall(r'\d', follower_str, re.MULTILINE))))
        except:
            followers.append(0)
        try:
            ratings.append(float(soup.find("span", itemprop="ratingValue").text.strip()))
        except:
            ratings.append(0)
        try:
            genres.append(soup.findAll("div", {"class": "elementList"})[0].a.get_text())
        except:
            genres.append('Unknown')
        try:
            bindings.append(soup.find("span", itemprop="bookFormat").text.strip())
        except:
            bindings.append('Unknown Binding')
        try:
            page_num.append(int(soup.find("span", itemprop="numberOfPages").text.strip(' pages')))
        except:
            page_num.append(np.nan)
        try:
            date_string = soup.findAll("div", {"class": "row"})[1].get_text()
            dates.append(int(re.search(r"(\d{4})", date_string, re.MULTILINE).group(0)))
        except:
            dates.append('')
        try:
            og_date_string = soup.findAll("div", {"class": "row"})[1].get_text()
            og_dates.append(int(re.findall(r"(\d{4})", og_date_string, re.MULTILINE)[1]))
        except:
            og_dates.append('')
        try:
            lang.append(soup.find("div", itemprop="inLanguage").text)
        except:
            lang.append('Unknown')
        try:
            num_likes.append(int(re.findall(r'<span class=\\\"value\\\">(.*)<\\/span>% of people liked it',
                                            str(soup), re.MULTILINE)[0]))
        except:
            num_likes.append(0)
        try:
            trivia_qs.append(int(re.search(r'\d+', soup.findAll("div", {"class": "mediumText"})[1].get_text()).group()))
        except:
            trivia_qs.append(0)
        try:
            quote_likes.append(int(re.search(r'\d+',
                                             soup.findAll("a", {"class": "actionLinkLite"})[-2].get_text()).group()))
        except:
            quote_likes.append(0)
        try:
            rev_likes.append(int(re.search(r'\d+', soup.select('a[id*="like_count_review"]')[0].get_text()).group()))
        except:
            rev_likes.append(0)
        try:
            num_rate_str = soup.find("meta", itemprop="ratingCount")
            num_ratings.append(int(num_rate_str["content"]))
        except:
            num_ratings.append(0)
        try:
            num_revs_str = soup.find("meta", itemprop="reviewCount")
            num_revs.append(int(num_revs_str["content"]))
        except:
            num_revs.append(0)
        # if i + 1 % 150 == 0:
        #     time.sleep(320)
        time.sleep(2)
    keys = ['book_num', 'title', 'author', 'followers', 'pub_date', 'og_pub_date', 'avg_rating', 'genre', 'binding',
            'pages', 'language', 'perc_like', 'trivia', 'quote_likes', 'rev_likes', 'num_revs', 'num_ratings']
    values = [book_nums, titles, authors, followers, dates, og_dates, ratings, genres, bindings, page_num, lang,
              num_likes, trivia_qs, quote_likes, rev_likes, num_revs, num_ratings]
    d = dict(zip(keys, values))
    book_df = pd.DataFrame(d)
    driver.close()
    print('Book scrape complete')
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
    print('Start book stats scrape')
    for i, book_reference_number in enumerate(ref_nums):
        print(i, book_reference_number)
        # if i + 1 % 150 == 0:
        #     time.sleep(320)
        time.sleep(2)
        stats_driver.get("https://www.goodreads.com/book/stats?id=" + str(book_reference_number))
        stats_soup = BeautifulSoup(stats_driver.page_source, 'lxml')
        try:
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
    num_samples = 2500
    random.seed(110)
    book_nums = random.sample(range(1, 8630000), num_samples)  # Last book is 8,630,000

    """Process and save dataframe"""
    book_df_raw = process_gr(book_nums)
    book_df_raw = book_df_raw.replace('', np.nan)
    with open('data/book_data.pkl', 'wb') as savefile:
        pickle.dump(book_df_raw, savefile)

    """Open and manipulate dataframe"""
    with open("data/book_data.pkl", 'rb') as openfile:
        book_df = pickle.load(openfile)
    print(book_df.describe())


if __name__ == "__main__":
    main()
