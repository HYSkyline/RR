# -*- coding:utf-8 -*-

import urllib
import urllib2
import time
import re
import cookielib
import sys


reload(sys)         # 重新载入sys库
sys.setdefaultencoding("utf-8")         # 将程序运行环境编码从默认的ascii码变为utf-8,便于使用中文输出

email = input(u'输入登录账号\n')          # 输入查询者的个人账号
password = input(u'输入登录密码\n')           # 输入查询者个人账户的密码
sleeping = float(input(u'输入每次访问的间隔时间(单位为秒)\n注意:间隔时间过小可能导致从网的封禁,默认为0s\n'))           # 设置每次读取信息之间的休眠时间

print "Link Start!"         # 开始连接！
t1 = time.time()            # 记录当前时间,准备计算程序运行总时长
error_list = []         # 准备错误列表,记录读取失败的目标(由于目标昵称内存在复杂字符同样会导致报错,因此不直接输出姓名)

ref = "http://m.renren.com/q.do?null"			# 写入访问来源
UserAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"			# 写入浏览器特征
postdata = {
    'email': email,
    'password': password,
    'ref': ref,
    'User-Agent':UserAgent
}			# 组织需要向网页提交的数据，形成字典
data = urllib.urlencode(postdata)           # 对提交数据进行编码

# 创建cookie
cookie = cookielib.CookieJar()
cookieHP = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(cookieHP)         # 建立虚假浏览器

targets = []            # 建立目标网页URL列表

login_url = "http://3g.renren.com"          # 开始登录从网
req = urllib2.Request(
    login_url,
    data
)			# 构建网页访问请求
response = opener.open(req)			# 打开网页
response_read = response.read()			# 获得查询者个人主页的网页源码
response.close()            # 关闭网页

login_check = '账号和密码不匹配(.*?)找回密码'           # 检查网页是否为密码错误页面,此处为检验变量
logincode_check = "为了您的账号安全(.*?)验证码"            # 检查网页是否为验证码页面,此处为检验变量
login_checkinfo = re.findall(login_check, response_read, re.S)          # 检查是否出现账号密码不匹配字样
logincode_checkinfo = re.findall(logincode_check, response_read, re.S)          # 检查是否出现验证码字样
if login_checkinfo:         # 如果出现账号密码不匹配字样
    print u"登录失败:账号/密码错误"       # 提示账号/密码错误
    print 'Link Logout.'            # 断开连接
    exit()          # 程序中止
elif logincode_check:           # 如果出现验证码字样
    print u"登录失败:验证码阻拦"         # 提示出现验证码错误
    print 'Link Logout.'            # 断开连接
    exit()          # 程序中止

f1_search = '>个人主页</a>.*?<a href="(.*?)">好友</a>'            # 此处为搜索好友列表网页URL的变量
f1_url = re.findall(f1_search, response_read, re.S)         # 搜索好友列表网页的URL地址,返回的f1_url[0]即为好友列表URL地址
req = urllib2.Request(
    f1_url[0],
    data
)           # 构建网页访问请求
response = opener.open(req)			# 打开网页
response_read = response.read()			# 获得好友列表网页源码
response.close()            # 关闭网页

f_pagenum_search = '第1/(.*?)页'          # 此处为搜索好友列表具体页数的变量
f_pagenum = re.findall(f_pagenum_search, response_read, re.S)           # 搜索共有多少页目标


for i in range(0, int(f_pagenum[0])):           # 按照页数对好友列表进行遍历
    login_url = f1_url[0][:35] + "curpage=" + str(i) + f1_url[0][35:]
    # 构建好友列表中每一页的URL
    req = urllib2.Request(
        login_url,
        data
    )			# 构建网页访问请求
    response = opener.open(req)			# 打开网页
    response_read = response.read()			# 获得好友列表各页的网页源码
    response.close()            # 关闭网页
    friend_url_search = '</td><td><a href="(.*?)">.*?</a><br />'
    friend_url = re.findall(friend_url_search, response_read, re.S)         # 获得目标个人主页URL
    for each in friend_url:
        targets.append(each.replace('amp;', 'htf=738&').replace('profile', 'details'))          # 构建目标详细资料页的URL,并添加至目标列表中
    print u"第" + str(i+1) + u"页目标网页地址采集完毕"          # 报告好友列表的读入进度
print u"已确认" + str(len(targets)) + u"个目标"           # 好友列表读取完成,报告本次任务的目标总数

name_search = '<title>手机人人网 - (.*?)</title>'            # 此处变量用于姓名搜索
info_search = '<b>基本信息</b></div><div>(.*?)</div></div><div class="sec">'            # 此处变量用于登录目标基本信息搜索(包括生日、星座、爱好等,从网将此类信息与最后登录时间一起作为个人基本信息)
date_search = r'</start>(.*?) (.*?) (.*?) (.*?) (.*?) (.*?)</end>'          # 此处变量用于区分最后登录时间中的年份、月份、日、星期(其中</start></end>为自定义符号)

weekdays = []           # 此处变量用于存储星期信息
months = []         # 此处变量用于存储月份信息
days = []           # 此处变量用于存储日期信息
times = []          # 此处变量用于存储具体时间信息
years = []          # 此处变量用于存储年份信息

f = open(r"D:\ctemp\ttimeinfo010101.txt", 'w')          # 创建存储文件,用于记录信息(a为追加模式,w为只写模式,在w模式下每次打开会抹去上一次的所有记录)

for i in range(0, len(targets)):            # 按顺序对目标详细资料网页进行遍历
    req = urllib2.Request(
        targets[i],
        data
    )			# 构建网页访问请求
    response = opener.open(req)			# 打开网页
    response_read = response.read()			# 获得目标详细资料网页源码
    response.close()            # 关闭网页
    name = re.findall(name_search, response_read, re.S)         # 读取目标姓名
    info = re.findall(info_search, response_read, re.S)         # 读取目标基本信息
    time_search = '<br />最后登录：(.*?)<br />'          # 此处变量用于在基本信息中读取最后登录时间信息
    try:
        time_info = re.findall(time_search, info[0], re.S)          # 读取目标最后登录时间
        date_info = '</start>' + time_info[0] + '</end>'            # 构建最后登录时间的特定格式m用于提取不同尺度的时间信息
        date = re.findall(date_search, date_info, re.S)             # 读取最后登录时间中的年月日时和星期信息
        # 对星期信息进行处理,使之由原有的英文信息变为相应数字
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
        # 对月份信息进行处理,使之由原有的英文信息变为相应数字
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
        # 将相应信息添加至相应列表中,准备输出
        days.append(date[0][2])
        times.append(date[0][3])
        years.append(date[0][5])
        f.writelines(name[0] + '\t' + str(years[i]) + '\t' + str(months[i]) + '\t' + str(days[i]) + '\t' + times[i] + '\t' + str(weekdays[i]))          # 输出目标姓名与最后登录信息,以制表符相隔
        f.writelines('\n')          # 写完一个目标后换行
        print name[0] + u'的信息读取完成.  已完成%.2f' % (float(i+1)/len(targets)) + '%'          # 报告目标完成情况与当前进度
    except Exception as e:          # 此处为报错集合
        if str(e).find('list index out of range'):
            print u'第' + str(i + 1) + u'个目标读取失败,错误来源于从网封禁'          # 封禁导致读取到的信息为空,而在输出时产生对空列表的操作,因此报错为列表索引超出范围
        elif str(e).find('gbk') != -1:
            print u'第' + str(i + 1) + u'个目标读取失败,错误来源于目标姓名中包含未知的复杂字符'            # 目标姓名中包含非GBK系列的其他字符,无法写入文件
        else:
            print u'第' + str(i + 1) + u'个目标读取失败,错误来源于' + str(e)         # 其他错误报告
        error_list.append(str(i + 1))           # 将读取失败的目标记录在错误列表中
    time.sleep(sleeping)            # 读取间隔时间设置

t2 = time.time()            # 获得读取过程结束的时间
time_cost = t2-t1           # 计算读取过程所耗时间
print '\n'
print "Link Report:"            # 输出任务报告
print u"总耗时长" + str(time_cost) + u"秒"           # 耗时报告
print u'总计' + str(len(targets)) + u'个目标,成功读取%.3f' % (float(len(targets) - len(error_list)) / len(targets)) + '%'            # 完成率报告
seq = '、'
print u'第' + seq.join(error_list) + u'个目标读取失败'          # 读取失败的目标列表
print '\n'
print "Link Logout."            # 连接结束
