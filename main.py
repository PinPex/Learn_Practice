from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sqlite3 as s3


def find_cript(name, conn):
    cur.execute("SELECT * FROM Coins WHERE LOWER(coinName) LIKE ?", ('{}%'.format(name),))
    one_result = cur.fetchall()
    if one_result is not None:
        for i in one_result:
            print(*i)
    else:
        print("This crypt is not exist(or is not on website yet)")


if __name__ == "__main__":

    names = []
    prices = []
    cap = []
    conn = s3.connect('coins.db')

    cur = conn.cursor()

    cur.executescript('drop table if exists Coins;')

    cur.execute("""CREATE TABLE IF NOT EXISTS Coins(
       coinId INT PRIMARY KEY,
       coinName TEXT,
       coinPrice_in_$ REAL,
       coinCap_in_$ REAL);
    """)
    conn.commit()
    get_column_names = conn.execute("select * from Coins limit 1")
    col_name = [i[0] for i in get_column_names.description]
    print(*col_name)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
    driver.get("https://coinmarketcap.com/")
    try:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        pages_n = (int)(re.sub(r"[\[\]]", "", re.sub(r'<.*?>', ' ', str(soup.find_all('li', class_ ='page'))).split(',')[11]))
        num = 100

        for pages in range(0, pages_n):

            if pages == 0:
                url = "https://coinmarketcap.com/"
            else:
                url = "https://coinmarketcap.com/?page=" + str(pages + 1)

            driver.get(url)
            y = 100
            for timer in range(0, 500):
                driver.execute_script("window.scrollTo(0, " + str(y) + ")")
                y += 100
            soup = BeautifulSoup(driver.page_source, 'lxml')

            if pages == pages_n - 1:
                num = re.sub(r"[\[\]]", "",
                             re.sub(r'<.*?>', ' ', str(soup.find_all('p', class_='sc-1eb5slv-0 etpvrL')))).split(', ')
                num = (int)(num[len(num) - 1]) - pages * 100

            names.append(re.sub(r'<.*?>', ' ', str(soup.findAll(True, {
                'class': ['sc-1eb5slv-0 iworPT', 'sc-1eb5slv-0 iworPT rise', 'sc-1eb5slv-0 iworPT fall', ]}))).split(','))
            names[pages] = names[pages][9:]
            for i in range(0,num):
                names[pages][i] = names[pages][i].strip()
            names[pages][num - 1] = re.sub(r"[\[\]]", "", names[pages][num - 1]).strip()
            prices.append(
                re.sub(r'<.*?>', ' ', str(soup.findAll(True, {
                    'class': ['sc-131di3y-0 cLgOOr', 'sc-131di3y-0 cLgOOr rise', 'sc-131di3y-0 cLgOOr fall']}))).split(
                    ', '))

            if(pages < 12):
                prices[pages] = prices[pages][3:]
            prices[pages][0] = re.sub(r'[\[\]]', '', prices[pages][0]).strip()
            prices[pages][num - 1] = re.sub(r'[\[\]]', '', prices[pages][num - 1]).strip()
            for i in range(0, num):
                prices[pages][i] = re.sub('[^\d\.]', '', prices[pages][i])
                prices[pages][i] = prices[pages][i].replace(",", "")
                prices[pages][i] = prices[pages][i].replace("...", "000")
            cap.append(
                re.sub(r'<.*?>', ' ', str(soup.findAll(True, {
                    'class': ['sc-1ow4cwt-1 ieFnWP', 's8fs2i-2 TBaWj', 'sc-1ow4cwt-1 ieFnWP rise',
                              'sc-1ow4cwt-1 ieFnWP fall']}))).split(', '))
            cap[pages][0] = re.sub(r'[\[\]]', '', cap[pages][0]).strip()
            cap[pages][num - 1] = re.sub(r'[\[\]]', '', cap[pages][num - 1]).strip()
            for j in range(0, num):
                cap[pages][j] = re.sub('[^\d\.]', '', cap[pages][j])
                cap[pages][j] = cap[pages][j].replace(",", "")
                cap[pages][j] = cap[pages][j].replace("...", "000")
                if not cap[pages][j].strip():
                    cap[pages][j] = "0"
            for i in range(0, num):
                cur.execute("INSERT INTO Coins VALUES(?,?,?,?);", (i + 1 + pages * 100, names[pages][i],
                                                                   (float)(prices[pages][i]), (float)(cap[pages][i])))
                conn.commit()
                cur.execute("SELECT * FROM Coins WHERE coinId LIKE ? ;", [(str)(i + 1 + pages * 100)])
                one_result = cur.fetchone()

                print(*one_result)
        driver.quit()
        while True:
            name = input()
            find_cript(name, conn)
    except KeyboardInterrupt:
        driver.quit()
