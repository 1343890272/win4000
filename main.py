import sys
from threading import Thread
import requests
from bs4 import BeautifulSoup
import re

url = 'http://www.win4000.com'
req = requests.Session()
l_zt = []
l_zt_o = []
l_d = []
l_d_o = []
l_i = []


def s():
    """
    爬取首页
    找分类
    :return:
    """
    # 第一层
    r = req.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    Thread(target=find_zt, args=(soup,)).start()


def find_zt(soup):
    """
    找到分类加入l_zt
    :param soup:
    :return:
    """
    zt = soup.find_all('a', href=re.compile('.*?/.*?zt/(.*?).html'))
    if len(zt) != 0:
        for i in zt:
            title = i.text.strip()
            if title == '':
                try:
                    title = i.find('img')['title']
                except:
                    title = i.parent.find('a').text.strip()
                    if title == '':
                        title = i.parent.text.strip()
            href = i['href']
            if not 'http://www.win4000.com' in href:
                href = 'http://www.win4000.com' + href
            if href not in [i['href'] for i in l_zt_o] and href not in [i['href'] for i in l_zt]:
                l_zt.append({'title': title, 'href': href})


def detail(args):
    """
    壁纸集找壁纸
    :return:
    """
    # 第三层
    title_zt = args[0]['title']
    href_zt = args[0]['href']  # zt
    title_detail = args[1]['title']
    href_detail = args[1]['href']  # detail
    j = 0
    front = href_detail[:-5]
    behind = href_detail[-5:]
    # 页
    while True:
        j += 1
        href_detail = front + f'_{j}' + behind
        r = req.get(href_detail)
        r.encoding = 'utf-8'
        if r.status_code == 404:
            break
        soup = BeautifulSoup(r.text, 'html.parser')
        Thread(target=find_zt, args=(soup,)).start()
        img = soup.find('img', class_='pic-large')
        img_title = img['title']
        img_url = img['src']
        k = {'title': title_zt, 'href': href_zt, 'next': {'title': title_detail, 'href': href_detail,
                                                          'next': {'title': img_title, 'href': img_url}}}
        if k not in l_i:
            l_i.append(img_url)
        sys.stdout.write(
            f'\r分类队列:{str(len(l_zt))},分类:{str(len(l_zt_o))},壁纸集:{len(l_d_o)},图片:{len(l_i)}')
        sys.stdout.flush()
        if len(l_i) != 0:
            try:
                f = open('1.json', 'w', encoding='utf-8')
                f.write(str(l_i).replace("'", '"'))
            finally:
                f.close()
        # print(title_zt + '>' + title_detail + '>' + img_title + '>' + img_url)


def zt(args):
    """
    分类找壁纸集
    :param args:
    :return:
    """
    # 第二层
    title_zt = args['title']
    href_zt = args['href']  # zt
    j = 0
    front = href_zt[:-5]
    behind = href_zt[-5:]
    # 页
    while True:
        j += 1
        href_zt = front + f'_{j}' + behind
        r = req.get(href_zt)
        r.encoding = 'utf-8'
        if r.status_code == 404:
            break
        soup = BeautifulSoup(r.text, 'html.parser')
        Thread(target=find_zt, args=(soup,)).start()
        for i in soup.find_all('a', href=re.compile('http://www.win4000.com/wallpaper_detail_(.*?).html')):
            title_detail = i['title']
            href_detail = i['href']
            k = {'title': title_detail, 'href': href_detail}
            l_d.append(k)
            Thread(target=detail,
                   args=([{'href': href_zt, 'title': title_zt}, {'href': href_detail, 'title': title_detail}],)).start()
            l_d_o.append(k)
            l_d.remove(k)


if __name__ == '__main__':
    # 第一层
    s()
    # 第二层
    t = {}
    while True:
        if len(l_zt) != 0:
            for i in l_zt:
                Thread(target=zt, args=(i,)).start()
                l_zt_o.append(i)
                l_zt.remove(i)
