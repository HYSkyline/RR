# -*- coding:utf-8 -*-

import urllib
import urllib2
import time
import re
import cookielib
import sys

reload(sys)
# print sys.getdefaultencoding()
sys.setdefaultencoding("utf-8")
# print sys.getdefaultencoding()

print "Link Start!"
t1 = time.time()
error_list = []

email = input(u'输入登录账号')
password = input(u'输入登录密码')
ref = "http://m.renren.com/q.do?null"			# 写入访问来源
UserAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"			# 写入浏览器特征
postdata = {
    'email': email,
    'password': password,
    'ref': ref,
    'User-Agent': UserAgent
}			# 组织需要向网页提交的数据，形成字典
data = urllib.urlencode(postdata)           # 对提交数据进行编码

# 创建cookie
cookie = cookielib.CookieJar()
cookieHP = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(cookieHP)

# 创建文本文档，准备存储好友信息
targets = []

ranger = input(u'输入目标数量')
init_id = input(u'输入第一个目标的ID(输入0则默认为338439969)')
if init_id == 0:
    init_id = 338439969
final_id = init_id + ranger
for i in range(init_id, final_id):
    target = 'http://3g.renren.com/details.do?id=' + str(i) + '&htf=738&sid=9s2rB_0HVrp1WYcJGhQ6AM&qg5ups'
    targets.append(target)
print u"已确认" + str(len(targets)) + u"个目标"

name_search = '<title>手机人人网 - (.*?)</title>'
info_search = '<b>基本信息</b></div><div>(.*?)</div></div><div class="sec">'
date_search = r'</start>(.*?) (.*?) (.*?) (.*?) (.*?) (.*?)</end>'

weekdays = []
months = []
days = []
times = []
years = []

f = open(r"D:\ctemp\ttimeinfo0101.txt", 'w')

for i in range(0, len(targets)):
    req = urllib2.Request(
        targets[i],
        data
    )			# 构建网页访问请求
    response = opener.open(req)			# 打开网页
    response_read = response.read()			# 获得好友列表网页源码
    response.close()            # 关闭网页
    name = re.findall(name_search, response_read, re.S)
    info = re.findall(info_search, response_read, re.S)
    time_search = '<br />最后登录：(.*?)<br />'
    try:
        time_info = re.findall(time_search, info[0], re.S)
        date_info = '</start>' + time_info[0] + '</end>'
        date = re.findall(date_search, date_info, re.S)

        if date[0][0].find('Mon') != -1:
            weekdays.append('01')
        elif date[0][0].find('Tue') != -1:
            weekdays.append('02')
        elif date[0][0].find('Wed') != -1:
            weekdays.append('03')
        elif date[0][0].find('Thu') != -1:
            weekdays.append('04')
        elif date[0][0].find('Fri') != -1:
            weekdays.append('05')
        elif date[0][0].find('Sat') != -1:
            weekdays.append('06')
        elif date[0][0].find('Sun') != -1:
            weekdays.append('07')

        if date[0][1].find('Jan') != -1:
            months.append('01')
        elif date[0][1].find('Feb') != -1:
            months.append('02')
        elif date[0][1].find('Mar') != -1:
            months.append('03')
        elif date[0][1].find('Apr') != -1:
            months.append('04')
        elif date[0][1].find('May') != -1:
            months.append('05')
        elif date[0][1].find('Jun') != -1:
            months.append('06')
        elif date[0][1].find('Jul') != -1:
            months.append('07')
        elif date[0][1].find('Aug') != -1:
            months.append('08')
        elif date[0][1].find('Sep') != -1:
            months.append('09')
        elif date[0][1].find('Oct') != -1:
            months.append('10')
        elif date[0][1].find('Nov') != -1:
            months.append('11')
        elif date[0][1].find('Dec') != -1:
            months.append('12')

        days.append(date[0][2])
        times.append(date[0][3])
        years.append(date[0][5])

        f.writelines(name[0] + '\t' + str(years[i]) + '\t' + str(months[i]) + '\t' + str(days[i]) + '\t' + times[i] + '\t' + str(weekdays[i]))
        f.writelines('\n')
        print name[0] + u'的信息读取完成.  已完成%.3f' % float((i + 1) * 100 /float(len(targets))) + u'%,当前目标ID：' + str(i + init_id)
    except Exception as e:
        print u'第' + str(i + init_id) + u'号目标读取失败,错误来源于' + str(e)
        error_list.append(str(i + init_id))

t2 = time.time()
time_cost = t2-t1
print '\n'
print "Link Report:"
print u"总耗时长%.3f" % float(time_cost) + u"秒"
if len(targets) != 0:
    print u'总计' + str(len(targets)) + u'个目标,成功读取其中%.3f' % float(float(len(targets) - len(error_list)) * 100 / float(len(targets))) + u'%'
if len(error_list) != 0:
    seq = '、'
    print u'第' + seq.join(error_list) + u'号目标读取失败'
print '\n'
print "Link Logout."
