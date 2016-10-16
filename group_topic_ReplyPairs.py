"""
Given the douban group id, and get all the the reply pairs in every topic of this group
Command line : ***.py group_id
Command line(restart): python group_topic_ReplyPairs.py group_id topic_id
"""

from lxml import etree
import requests
from reply_pairs import Reply_Pairs
import os
import sys
import time


class Group_Topic_ReplyPairs:
    def __init__(self, baseurl, path, group_id):
        self.baseurl = baseurl
        self.path = path
        self.group_id = group_id

    def g_pre_process(self, url):  # get g_selector and g_flag
        time.sleep(2)
        g_webpage = requests.get(url)
        g_tree = etree.HTML(g_webpage.text)
        g_selector = g_tree.xpath('//tr[@class=""]//td[@class="title"]//a/@href')  # https://www.douban.com/group/topic/87036370/
        g_flag = len(g_tree.xpath('//table[@class="olt"]'))
        return g_selector, g_flag  # g_selector: the list of full links of topics in one page

    def call_reply_pairs(self, each):  # each: the full link of a topic
        topic_id = each[-9:-1]  # eg: https://www.douban.com/group/topic/87036370/
        rp = Reply_Pairs(baseurl=each)
        Pairs = rp.get_pairs()  # call class Reply_Pairs to get all the reply pairs in one topic
        if len(Pairs) != 0:  # make sure there wont be any empty txt
            title = "{0}/{1}{2}".format(self.path, topic_id, ".txt")
            print "{0}{1}".format("Processing topic ", topic_id)
            with open(title, 'w') as f:
                for p in Pairs:
                    f.write(p.encode('utf-8'))
                    f.write('\n')

    def process_topics_in_one_page(self, g_flag, p, g_count, g_selector):
        while g_flag != 0:  # get into the process of topics in one page
            p += 1
            print "{0}{1}".format("Processing page ", p)
            for g_each in g_selector:
                self.call_reply_pairs(g_each)
            g_count += 25
            newurl = "{0}{1}{2}{3}".format("https://www.douban.com/group/", self.group_id, "/discussion?start=", g_count)  # get the link of next page of topic table
            g_selector, g_flag = self.g_pre_process(newurl)

    def g_get_pairs(self, start_from_id=None):

        if start_from_id == None:  # if its not restart mode
            g_selector, g_flag = self.g_pre_process(self.baseurl)
            p = 0
            g_count = 0
            self.process_topics_in_one_page(g_flag, p, g_count, g_selector)

        else:
            g_selector, g_flag = self.g_pre_process(self.baseurl)
            p = 0
            g_count = 0

            while g_flag != 0:  # get into the process of topics in one page
                p += 1
                start_from_link = "{0}{1}/".format("https://www.douban.com/group/topic/", start_from_id)  # str
                if start_from_link in g_selector:
                    print "{0}{1}".format("Processing page ", p)
                    position = g_selector.index(start_from_link)  # get the position of the restart topic link in the list that stores all the topic link
                    for i in range(position, len(g_selector)):  # start to get reply pairs from this position
                        self.call_reply_pairs(g_selector[i])
                    break
                g_count += 25
                newurl = "{0}{1}{2}{3}".format("https://www.douban.com/group/", self.group_id, "/discussion?start=", g_count)  # get the link of next page of topic table
                g_selector, g_flag = self.g_pre_process(newurl)

            g_count += 25
            newurl = "{0}{1}{2}{3}".format("https://www.douban.com/group/", self.group_id, "/discussion?start=", g_count)  # get the link of next page of topic table
            g_selector, g_flag = self.g_pre_process(newurl)
            self.process_topics_in_one_page(g_flag, p, g_count, g_selector)



if __name__ == '__main__':

    # url = 'https://www.douban.com/group/10658/discussion?start=0'
    # group_id = '10658'

    group_id = sys.argv[1]  # type:str
    baseurl = "{0}{1}{2}".format("https://www.douban.com/group/", group_id, "/discussion?start=0")
    path = "{0}{1}".format("Group_Topic_ReplyPairs_Results/", group_id)
    if not os.path.exists(path):
        os.makedirs(path)
    gtr = Group_Topic_ReplyPairs(baseurl=baseurl, path=path, group_id=group_id)
    if len(sys.argv) == 3:
        gtr.g_get_pairs(sys.argv[2])
    else:
        gtr.g_get_pairs()


