# -*- coding:utf-8 -*-
import urllib
import urllib2
import cookielib
import re
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

print "Link Start!"
print ""
t0 = time.time()

# 输入用户名与密码
email = input(u'输入登录账号\n')          # 输入查询者的个人账号
password = input(u'输入登录密码\n')           # 输入查询者个人账户的密码
sleeping = float(input(u'输入每次访问的间隔时间(单位为秒)\n注意:间隔时间过小可能导致从网的封禁,默认为0s\n'))           # 设置每次读取信息之间的休眠时间

# 构建cookie与启动器opener
cookie = cookielib.CookieJar()			# 生成CookieJar实例
cookie_Hp = urllib2.HTTPCookieProcessor(cookie)			# 
opener = urllib2.build_opener(cookie_Hp)			# 根据cookie_Hp构建打开模式

# 开始读取源码
url = 'http://www.renren.com/PLogin.do'			# 输入登录网站地址
postdata = {
    'email': email,
    'password': password,
    'domain': domain
}			# 准备传输所需要的数据
data = urllib.urlencode(postdata)			# 将所需要的数据按照网站阅读格式处理
req = urllib2.Request(
    url,
    data
)			# 将访问网站与所需数据结合，构建一个全面的访问请求
response = opener.open(req)         # 用上文自主构建的打开模式来访问网站
response_read = response.read()
try:
    
    # 搜索人品网页
    renpin_url_search = 'target="_blank"></a><a href="(.*?)" target="_blank" class="for_content">'			# 输入用于确定人品网站地址的正则表达式
    renpin_url = re.findall(renpin_url_search, response_read, re.S)			# 以正则表达式匹配主页面源码，生成含人品网页地址的一个列表
    # 读取人品网页源码
    RP_response = opener.open(renpin_url[0])			# 以上文自主构建的打开模式打开人品网页

    # 读取当日人品列表
    try:
		renpin_list_search = '</a><div class="name"><a target="_blank" href="http://www.renren.com/.*?">(.*?)</a></div><div class="score">(.*?)</div></li>'			# 输入用于读取人品列表数据的正则表达式
		renpin_list = re.findall(renpin_list_search,RP_response.read(),re.S)			# 以正则表达式来匹配人品网页源码，获取人品数据的列表
		# for each in renpin_list:			# 测试所得内容是否正确
		#     print each[0].decode('utf-8')+"--->"+str(each[1])

		time_now=time.strftime('%Y%m%d',time.localtime(time.time()))
		minutes_now = time.strftime('%H:%M:%S',time.localtime(time.time()))
		# 写入文件
		print "Link Report:"
		fpath = r"F:\application\python\RR\rr_rp_result.txt"			# 输入文件保存信息
		f=open(fpath,'a')			# 以追加模式打开文件，准备输入今天的信息
		for each in renpin_list:			#按人品列表中的各项数据进行循环
			f.writelines((each[0].decode('utf-8')).encode('gb18030')+"\tscore:\t"+str(each[1])+ "\t" + str(minutes_now) + "\t" + str(time_now))			# 写入各项数据(列表为二维，第一维为人名，第二维为人品值)
			print each[0].decode('utf-8') + '\t' + 'score:' + each[1] + '\tdetected.'
			f.writelines('\n')			# writelines没有自动换行功能，因此手动写入换行符
		f.close()			# 关闭文件，程序执行完成
    except Exception as ee:
        print u"RP值读取失败:" + str(ee)
except Exception as e:
    print "网页读取错误" + str(e)

t1 = time.time()
time_cost = t1 - t0
print "Time used:%3f" % float(time_cost) + "s"
print ""
print "Link Logout."