import asyncio
import os.path
import requests
from lxml import etree
import aiohttp

# 获取全部章节和子章节链接
def get_child_url(base_url):
    response = requests.get(url=base_url)
    # print(response.text)
    # //*[@id="list"]
    resp_text = etree.HTML(response.text)
    xpath_list = resp_text.xpath('//*[@id="list"]/dl//dd/a')
    # print(xpath_list)
    # # xpath_list = resp_text.xpath('//*[ @id ="list"]/dl/dd[13]/a')# 第一章的列表
    url_list = []
    for li in xpath_list:
        # 获取章节名称和url链接，然后拼接章节名称和  url
        url_list.append(li.xpath('./@href') + li.xpath('./text()'))
        # url_list.append(li.xpath('./@href'))
    return url_list

# 这里进行协程程序的调用，将章节名称和 修复的url传过去
def name_url(url_list):
    # name_urls = []
    tasks=[]
    for url in url_list:
        if url[0][:5] != "https":
            requests_url = "https://www.bxwxorg.com" + url[0]
            name = url[1] + '.txt'
            c = download(name, requests_url)
            # print(name, requests_url)
            task = asyncio.ensure_future(c)
            tasks.append(task)
            # download(requests_url)
    return tasks
# 下载子章节内容
# https://www.bxwxorg.com/read/11/655303.html  第一章
# https://www.bxwxorg.com/read/11/657380.html  最后一章
async def download(name, requests_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(requests_url) as resp:
            # resp = requests.get(requests_url)     # 这里写的不对，所以没法通过协程去加快速度了
            resp_text = await resp.text()
            # 解析页面内容
            html = etree.HTML(resp_text)
            # # 获取文本内容
            text = html.xpath('//*[@id="content"]/p[not(contains(@style, "color:"))]/text()')
            # # 将text中获得全文，拼接起来, 除了第0个元素不要，后面的拼接起来。
            text1 = " ".join(text[1:])
            with open(f'd:\莽荒纪1\{name}', 'w') as fp:
                fp.write(text1)

if __name__ == '__main__':
    # # 本地保存路径
    if not os.path.exists(r'd:\莽荒纪1'):
        os.mkdir(r'd:\莽荒纪1')
    base_url = "https://www.bxwxorg.com/read/11/"
    # 获取url
    url_list = get_child_url(base_url)
    tasks = name_url(url_list)
    # download(url_list)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))