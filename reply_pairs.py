"""
Given the douban topic id, and get all the reply pairs in this topic
"""

from lxml import etree
import requests
import urllib
import time


class Reply_Pairs:
    def __init__(self, baseurl):
        self.baseurl = baseurl

    def pre_process(self, url):
        time.sleep(2)
        webpage = requests.get(url)
        tree = etree.HTML(webpage.text)
        selector = tree.xpath('//ul[@class="topic-reply"]//div[@class="reply-quote"]')  # type:list  # get all the nodes which have reply
        flag = len(tree.xpath('//ul[@class="topic-reply"]//div[@class="reply-quote"]//span[@class="all"]'))  # use to determine whether there is a page with reply after this page
        return selector, flag

    def get_pairs(self):
        selector, flag = self.pre_process(self.baseurl)
        pairs = []  # use to store the final pairs
        count = 0

        while flag != 0:  # when flag ==0, there isnt any page with reply after this page, so break out of the while loop
            for each in selector:
                str_be_reply_tem = each.xpath('span[@class="all"]/text()')  # list with one item,  a sentence that is replied
                str_reply_tem = each.xpath('following-sibling::p/text()')  # list with one item,   a sentence that reply

                # str_be_reply_tem[0] = str_be_reply_tem[0].encode('utf-8')
                # delete space \r\n between every reply_sentences and every be_reply_sentences
                str_temp_be = ' '.join(str_be_reply_tem[0].split('\r\n'))
                str_temp = ' '.join(str_reply_tem)
                pairs.append(str_temp_be + '\t' + str_temp)  #concatenate a reply_sentence and the correspongding be_reply_sentence

            count += 100
            url = self.baseurl + "?start=" + str(count)  # get the next web pages link
            newurl = url
            selector, flag = self.pre_process(newurl)
        return pairs



    def get_webpage(self, url):
        htmlSource = urllib.urlopen(url).read()
        with open('webpage.html', 'w') as f:
            f.write(htmlSource)


if __name__ == '__main__':
    #url = 'https://www.douban.com/group/topic/90151868/'
    id = raw_input("Input douban topic id: ")
    baseurl = 'https://www.douban.com/group/topic/' + str(id)
    rp = Reply_Pairs(baseurl=baseurl)
    Pairs = rp.get_pairs()
    #pw.get_webpage()

    with open('Douban_ReplyPairs.txt', 'w') as f:
        for p in Pairs:
            f.write(p.encode('utf-8'))
            f.write('\n')