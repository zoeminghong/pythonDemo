# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
from scrapy.http.request import Request
from scrapy.selector import Selector
from scrapy.exceptions import NotSupported
from scrapy import log
from imooc.items import ImoocItem
import urlparse
import json
import urllib

class ImoocMv(CrawlSpider):
    name = 'ImoocMv'
    start_urls=['http://www.imooc.com/course/list']

    def parse(self, response):
        """
        爬虫默认入口，旨在获取所有视频教程的 标题 以及 详细页 数据
        """
        sel = Selector(response)

        # 获取本页所有视频节点
        nodes = sel.xpath('//ul/li[@class="course-one"]')
        for node in nodes:
            try:
                title = node.xpath('./a/h5/span/text()').extract()[0]  #选取当前节点
                href = node.xpath('./a/@href').extract()[0]
                href = urlparse.urljoin(response.url, href) #response.url可以获取当前url

                # 将 url 中的 view -> learn 即可得到 视频详细页列表
                href = href.replace(u'view', u'learn')
                if title and href:
                    yield Request(
                        url=href,
                        callback=self.parse_list,
                        meta={'title': title}
                    )
            except(IndexError, TypeError):
                continue

        # 多页情况
        pages = sel.xpath('//div[@class="page"]/a[@href]')
        for page in pages:
            try:
                href = page.xpath('./@href').extract()[0]
                href = urlparse.urljoin(response.url, href)
                if href and href.startswith('http'):
                    yield Request(
                        url=href,
                        callback=self.parse,
                    )
            except(IndexError, TypeError, NotSupported):
                continue

    def parse_list(self, response):
        """
        视频列表页 解析
        :param response:
        :return:
        """

        """
        {"result":0,"data":{"result":{"mid":8124,"mpath":
        ["http:\/\/v1.mukewang.com\/f9fd506a-bf14-4ede-96c4-1d69d2fd26e7\/H.mp4",
        "http:\/\/v1.mukewang.com\/f9fd506a-bf14-4ede-96c4-1d69d2fd26e7\/M.mp4",
        "http:\/\/v1.mukewang.com\/f9fd506a-bf14-4ede-96c4-1d69d2fd26e7\/L.mp4"],
        "cpid":"2095","name":"NSMutableDictionary","time":"34","practise":[]}},"msg":"\u6210\u529f"}
        """
        # 查看js文件可以得到 视频地址获取接口如下 GET -> json
        pre_href = 'http://www.imooc.com/course/ajaxmediainfo/?mid={}'

        title = response.meta.get('title')

        sel = Selector(response)

        nodes = sel.xpath('//div[@class="chapter"]//ul[@class="video"]/li/a')

        videos = []
        item = ImoocItem()
        for node in nodes:
            try:
                section = node.xpath('./text()').extract()[0]
                section = section.strip().replace('\r', '').replace('\n', '')
                video_id = node.xpath('./@href').extract()[0]
                video_id = video_id.split('/')[-1]
                if section and video_id:
                    href = pre_href.format(video_id)
                    response = urllib.urlopen(href)
                    data = json.loads(response.read())
                    # 此处存在三种模式 0:超清 1:高清 2:普清
                    url = data['data']['result']['mpath'][0]
                    # videos.append({section: url})
                    item['title'] = title
                    item["url"]=url
                    item["content"]=section
                    yield item
            except(IndexError, TypeError, ValueError):
                continue




    def parse_details(self, response):
        pass
