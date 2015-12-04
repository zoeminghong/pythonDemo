# -*-coding:utf8-*-
import requests
import urllib.parse
import re


class ZhiLian(object):
    def __init__(self):
        print(u'开始爬取内容。。。')

    # getsource用来获取网页源代码
    def getsource(self, url):
        html = requests.get(url)
        html.encoding = "utf-8"
        return html.text

    # geteveryclass用来抓取每个课程块的信息
    def geteveryclass(self, source):
        everyclass = re.findall('(<table cellpadding="0" cellspacing="0" width="853" class="newlist">.*?</table>)',
                                source, re.S)
        return everyclass

    # getinfo用来从每个课程块中提取出我们需要的信息
    def getinfo(self, eachclass):
        info = {}
        timeandlevel = re.findall('target="_blank">(.*?)</a>', eachclass, re.S)
        info['title'] = timeandlevel[0]
        info['company'] = timeandlevel[1]
        info['salary'] = re.search('class="zwyx">(.*?)</td>', eachclass, re.S).group(1)
        info['addr'] = re.search('class="gzdd">(.*?)</td>', eachclass, re.S).group(1)
        return info

    # saveinfo用来保存结果到info.txt文件中
    def saveinfo(self, classinfo):
        f = open('baidu.txt', 'a', encoding='utf-8')
        for each in classinfo:
            f.writelines('title:' + each['title'] + '\n')
            f.writelines('company:' + each['company'] + '\n')
            f.writelines('salary:' + each['salary'] + '\n')
            f.writelines('addr:' + each['addr'] + '\n\n')
        f.close()


if __name__ == '__main__':
    classinfo = []
    url = "http://sou.zhaopin.com/jobs/searchresult.ashx?"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'}
    param = {
        'bj': '160000',
        'sj': '009',
        'in': '210500%3B160400',
        'jl': '杭州',
        'p': '1',
        'isadv': 0
    }
    urlparam = urllib.parse.urlencode(param)
    url = url + urlparam
    zhiLian = ZhiLian()
    html = zhiLian.getsource(url)
    everyclass = zhiLian.geteveryclass(html)
    for each in everyclass:
        info = zhiLian.getinfo(each)
        classinfo.append(info)
    zhiLian.saveinfo(classinfo)
