#coding=utf-8
from lxml import etree
import requests
import time
import urllib
import sys


class Extract_Info:

    def __init__(self, baseurl):
        self.baseurl = baseurl

    def extract_info_in_one_ad(self, ad_url, id):
        time.sleep(30)
        webpage = requests.get(ad_url)
        tree = etree.HTML(webpage.text)

        """
        htmlSource = urllib.urlopen(ad_url).read()
        with open("{}{}".format(html, ".html"), 'w') as f:
            f.write(htmlSource)
        """

        # title
        title = tree.xpath('//div[@class="viewad-header new-common-version"]//div[@class="viewad-title "]//h1/text()')[0].encode("utf-8")
        # title = "".join(get_title).encode("utf-8")

        # service_content
        service_content = tree.xpath('//div[@class="viewad-meta2 new-fuwu-version"]//div[@class="viewad-meta2-item fuwu-content"]//div[@class="content"]//a/text()')  # []
        service_content_join = '-'.join(service_content).encode('utf-8')

        # service_coverage
        service_coverage = tree.xpath('//div[@class="viewad-meta2 new-fuwu-version"]//div[@class="viewad-meta2-item"]//div[@class="content"]//a/text()')
        service_coverage_join = '-'.join(service_coverage).encode('utf-8')

        # base_price
        tmp = tree.xpath('//div[@class="viewad-meta2 new-fuwu-version"]//div[@class="viewad-meta2-item"]')
        base_price = []
        for each in tmp:
            for label in each.xpath('label/text()'):
                if label.encode('utf-8') == "基价：":
                    get_base_price = each.xpath('div[@class="content"]//span/text()')
                    base_price = "".join(get_base_price).encode('utf-8')

        # information_content
        information_content = tree.xpath('//div[@class ="viewad-text-hide"]/text()')
        new = ''  # str
        for ic in information_content:
            new += ic
            new += ' '
        new_tmp = new.split('\r\n')
        information_content_join = ''.join(new_tmp).encode('utf-8')

        # datetime
        get_datetime = tree.xpath(
            '//div[@class="viewad-header new-common-version"]//div[@class="viewad-actions"]//span/@title')
        datetime = "".join(get_datetime)[6:].encode("utf-8")

        with open("vip_ads.txt", 'a')as f:
            f.write(
                "{},{},\"{}\",{},{},{},{}".format(id, title, information_content_join, service_content_join,
                                                  service_coverage_join, base_price, datetime))
            f.write('\n')

        print ("{} {}".format("Finish ", id))

            #return title, information_content_join, service_content_join, service_coverage_join, base_price, datetime

    def pre_process(self, newurl):
        time.sleep(30)
        webpage = requests.get(newurl)
        tree = etree.HTML(webpage.text)
        tmp = tree.xpath('//li')
        flag = []
        for each in tmp:
            for i in each.xpath('div//a/@data-original-title'):
                if i.encode('utf-8') == "服务VIP用户":
                    flag.append(each.xpath('@data-aid')[0])
                    break
        return flag

    def process_info_in_one_ad(self, flag, page):
        while flag != 0:
            print ("{}{}".format("Processing page ", page))
            for f in flag:
                id = str(f)
                ad_url = "{}{}{}".format("http://shanghai.baixing.com/banjia/a", id, ".html?src=reczone")
                self.extract_info_in_one_ad(ad_url=ad_url, id=id)
            page += 1
            newurl = "{}{}".format("http://shanghai.baixing.com/banjia/?page=", page)
            flag = self.pre_process(newurl=newurl)

    def get_ads_in_every_page(self, start_from_id=None):

        if start_from_id == None:  # if its not restart mode

            with open("vip_ads.txt", 'w')as f:
                f.write(
                    "{},{},{},{},{},{},{}".format("信息ID", "标题", "信息内容", "服务内容", "服务范围", "基价", "发布时间"))
                f.write('\n')
            flag = self.pre_process(newurl=self.baseurl)
            page = 1
            self.process_info_in_one_ad(flag=flag, page=page)

        else:
            flag = self.pre_process(newurl=self.baseurl)
            page = 1
            while flag != 0:
                for f in flag:
                    f = str(f)
                if start_from_id in flag:
                    print ("{}{}".format("Processing page ", page))
                    position = flag.index(start_from_id)
                    for i in range(position, len(flag)):
                        ad_url = "{}{}{}".format("http://shanghai.baixing.com/banjia/a", flag[i], ".html?src=reczone")
                        self.extract_info_in_one_ad(ad_url=ad_url, id=flag[i])
                    break
                page += 1
                newurl = "{}{}".format("http://shanghai.baixing.com/banjia/?page=", page)
                flag = self.pre_process(newurl=newurl)

            page += 1
            newurl = "{}{}".format("http://shanghai.baixing.com/banjia/?page=", page)
            flag = self.pre_process(newurl=newurl)

            self.process_info_in_one_ad(flag=flag, page=page)



if __name__ == '__main__':

    #url = "http://shanghai.baixing.com/banjia/a976037383.html?src=reczone"

    baseurl = "http://shanghai.baixing.com/banjia/?page=1"
    ei = Extract_Info(baseurl=baseurl)
    if len(sys.argv) == 2:
        ei.get_ads_in_every_page(sys.argv[1])
    else:
        ei.get_ads_in_every_page()
