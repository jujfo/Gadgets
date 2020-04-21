import requests
from retrying import retry
from bs4 import BeautifulSoup
from lxml import etree
import psutil
import time
import os
import platform
requests.packages.urllib3.disable_warnings()

@retry(stop_max_attempt_number=3)
def get_Response(url, **kwargs):

    response = requests.get(url, headers=headers,  params=kwargs, timeout=10)
    # print(response.url)
    if response.status_code == 200:
        response.encoding = response.apparent_encoding
        return response
    else:
        raise Exception("Error:", response.status_code)

def get_Soup(response):
    soup = BeautifulSoup(response.text, 'lxml')
    return soup

def get_Tree(response):
    tree = etree.HTML(response.text)
    return tree

def get_Picture_urls():
    for i in range(1, page_num+1):
        url = 'https://wallhaven.cc/random'
        new_url_response = get_Response(url, page=i)
        new_url_tree = get_Tree(new_url_response)
        picture_urls = new_url_tree.xpath('//*[@id="thumbs"]/section/ul/li/figure/a/@href')
        # print(picture_urls)
        yield picture_urls

def get_Picture_download_address(picture_url):
    picture_url_response = get_Response(picture_url)
    picture_url_soup = get_Soup(picture_url_response)
    src = picture_url_soup.find('img', id='wallpaper')['src']
    return src

def get_All_src():
    all_src = []
    for i in get_Picture_urls():
        # print(i)
        for u in i:
            # print(u)
            src = get_Picture_download_address(u)
            print(src)
            all_src.append(src)
    print('all_src:', len(all_src))
    return all_src

def get_Picture(all_src, system_type, file_names):
    if system_type == 'Windows':
        for i in all_src:
            name = i[-6:-4] + '-' + i[-10:-4]
            if name not in file_names:
                response = get_Response(i)
                f = open(path + r'\{}.png'.format(name), 'wb')
                f.write(response.content)
                f.close()
                print(name, '   下载成功')
            else:
                print(name, '   已存在，不进行下载')
    else:
        for i in all_src:
            name = i[-6:-4] + '-' + i[-10:-4]
            if name not in file_names:
                response = get_Response(i)
                f = open(path + r'/{}.png'.format(name), 'wb')
                f.write(response.content)
                f.close()
                print(name, '   下载成功')

def winDrivers():
    """
    Windows操作系统下,返回全部硬盘编号['C:\','D:\']
    :return: list
    """
    return sorted([driver.device for driver in psutil.disk_partitions(True)])

def judge_System_type():
    print('本机操作系统：' + platform.system())
    if platform.system() == 'Windows':
        if len(winDrivers()) > 1:
            path = winDrivers()[1] + "wallpaper"
        else:
            path = winDrivers()[0] + "wallpaper"
        if not os.path.exists(path):
            print('创建新文件夹')
            os.makedirs(path)
        print('新文件夹在:', path)
        return path, platform.system()
    else:
        path = os.getcwd() + '/wallpaper'
        if not os.path.exists(path):
            print('创建新文件夹')
            os.makedirs(path)
        print('新文件夹在:', path)
        return path, platform.system()

def get_File_names(path):
    file_names = []
    for files in os.walk(path):
        if len(files[-1]) > 0:
            for i in files[-1]:
                if i[-3:] == 'png':
                    file_names.append(i[0:-4])
            return file_names
        else:
            return file_names

if __name__ == '__main__':
    print('此程序是从 https://wallhaven.cc/random 下载随机桌面壁纸')
    path, system_type = judge_System_type()
    file_names = get_File_names(path)
    while True:
        print('-----开始-----')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
        }
        while True:
            try:
                page_num = int(input("请输入要下载的页数(1-12866)："))
                if 0 < page_num < 12867:
                    break
                else:
                    print('您输入的内容不规范，请重新输入')
            except:
                print('您输入的内容不规范，请重新输入')
        print('开始获取PNG地址')
        while True:
            try:
                all_src = get_All_src()
                print('获取PNG地址成功')
                break
            except:
                print('获取PNG地址失败')
                print('重新获取...')
        print('开始下载PNG')
        while True:
            try:
                get_Picture(all_src, system_type, file_names)
                print('获取所有PNG成功')
                break
            except:
                print('获取所有PNG失败')
                print('[1]重新下载所有PNG  [2]重新获取PNG地址')
                while True:
                    try:
                        choice = int(input('请输入相应的数字：'))
                        if choice == 2:
                            all_src = get_All_src()
                            print('获取PNG地址成功')
                            break
                        elif choice == 1:
                            print('开始下载PNG')
                            break
                        else:
                            print('您输入的内容不规范，请重新输入')
                    except:
                        print('您输入的内容不规范，请重新输入')
        print('-----结束-----')
        time.sleep(3)
        print('*' * 50)

## 后续会加上多进程什么的

