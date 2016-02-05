# -*- coding:utf-8 -*-

import urllib
import urllib2
import re
import time
import sys
import cookielib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.mime.application import MIMEApplication
from email.Header import Header
# from PIL import Image

reload(sys)
sys.setdefaultencoding("utf-8")


def main():
	email = raw_input('帐户名:'.decode('utf-8').encode('gbk'))
	password = raw_input('密码:'.decode('utf-8').encode('gbk'))
	mail_from = raw_input('通知起点:'.decode('utf-8').encode('gbk'))
	mail_password = raw_input('通知发送密码:'.decode('utf-8').encode('gbk'))
	mail_to = raw_input('手机号码(仅限移动):'.decode('utf-8').encode('gbk'))
	mail_to = mail_to + "@139.com"

	print "Link Start!"
	print "--" * 10
	t0 = time.time()
	rr_opener = opener_build()

	data = login_prepare(email, password)
	loginurl = "http://3g.renren.com"
	respose_read = login(loginurl, rr_opener, data)			# 确认登录，读取个人主页源码
	friend_urllist = friend_urllist_search(rr_opener, respose_read)			# 分析目标URL地址列表

	error_list = []
	friends = []
	for each in friend_urllist:
		friendinfo, error_target = friendpage_login(rr_opener, each)
		friends.append(friendinfo)
		if error_target:
			error_list.append(error_target)
	fpath = r"F:\application\python\RR\friendinfo160204.txt"
	time_write(fpath, friends)

	t1 = time.time()
	content = "(" + str(len(friend_urllist) - len(error_list)) + "/" + str(len(friend_urllist)) + ")\n"
	link_report(t0, t1, content=[error_list, content])
	mail_check = mail(mail_from, mail_password, mail_to, content, [fpath])
	t1 = time.time()
	link_report(t0, t1, content=["", mail_check])
	print "Link Logout."
	return 0


def login_prepare(email, password):
	ref = "http://m.renren.com/q.do?null"			# 写入访问来源
	useragent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
	postdata = {
		'email': email,
		'password': password,
		'ref': ref,
		'User-Agent':useragent
	}
	data = urllib.urlencode(postdata)
	return data


def login(url, opener, data):
	req = urllib2.Request(
		url,
		data
	)
	respose = opener.open(req)
	respose_read = respose.read()
	return respose_read


def friend_urllist_search(opener, read):
	f1_search = '>个人主页</a>.*?<a href="(.*?)">好友</a>'
	f1_url = re.findall(f1_search, read, re.S)
	req = urllib2.Request(
		f1_url[0]
	)
	respose = opener.open(req)
	friendlisturl_read = respose.read()

	f_pagenum_search = '第1/(.*?)页'
	f_pagenums = re.findall(f_pagenum_search, friendlisturl_read, re.S)           # 搜索共有多少页目标
	f_pagenum = int(f_pagenums[0])

	targets = []
	for i in range(f_pagenum):
		login_url = f1_url[0][:35] + "curpage=" + str(i) + f1_url[0][35:]
		req = urllib2.Request(
			login_url
		)
		respose_info = opener.open(req)
		info_read = respose_info.read()
		friend_url_search = '</td><td><a href="(.*?)">.*?</a><br />'
		friend_url = re.findall(friend_url_search, info_read, re.S)         # 获得目标个人主页URL
		for each in friend_url:
			targets.append(each.replace('amp;', 'htf=738&').replace('profile', 'details'))
		print u"第" + str(i+1) + u"页目标网页地址采集完毕"
	print u"已确认" + str(len(targets)) + u"个目标"
	print "--" * 10
	return targets


def friendpage_login(opener, url):
	error_target = ""
	req = urllib2.Request(
		url
	)
	response = opener.open(req)
	response_read = response.read()
	response.close()
	name = name_search(response_read)
	time_str = time_search(response_read)
	if time_str:
		time_check = True
	else:
		time_str = u"未知时间"
		error_target = name
	content = name + '\t' + time_str + '\n'
	return [content, error_target]


def name_search(response_read):
	name_search = '<title>手机人人网 - (.*?)</title>'
	names = re.findall(name_search, response_read, re.S)
	name = names[0]
	try:
		print name.decode('utf-8').encode('gbk'),
	except Exception as e:
		pass
	return name


def time_search(response_read):
	info_search = '<b>基本信息</b></div><div.*?>(.*?)</div></div><div class="sec">'
	infos = re.findall(info_search, response_read, re.S)
	info = infos[0]

	time_search = '最后登录：(.*?)<br />'
	login_time_list = []
	try:
		time_infos = re.findall(time_search, info, re.S)
		time_info = time_infos[0]

		date_search = r'</start>(.*?) (.*?) (.*?) (.*?) (.*?) (.*?)</end>'
		date_info = '</start>' + time_info + '</end>'
		date = re.findall(date_search, date_info, re.S)

		login_time_list.append(date[0][5])			# 年份信息
		login_time_list.append(month_transform(date[0][1]))			# 月份信息
		login_time_list.append(weekday_transform(date[0][0]))			# 星期信息
		login_time_list.append(date[0][2])			# 天数信息
		login_time_list.append(date[0][3])			# 具体时刻信息

		login_time = "\t".join(login_time_list)
		print u"分析完成"
		return login_time
	except Exception as e:
		print u"登录时间分析失败,错误对象:",
		print info.decode('utf-8').encode('gbk')
		return ""


def month_transform(m):
	if m.find('Jan') != -1:
		month = '01'
	elif m.find('Feb') != -1:
		month = '02'
	elif m.find('Mar') != -1:
		month = '03'
	elif m.find('Apr') != -1:
		month = '04'
	elif m.find('May') != -1:
		month = '05'
	elif m.find('Jun') != -1:
		month = '06'
	elif m.find('Jul') != -1:
		month = '07'
	elif m.find('Aug') != -1:
		month = '08'
	elif m.find('Sep') != -1:
		month = '09'
	elif m.find('Oct') != -1:
		month = '10'
	elif m.find('Nov') != -1:
		month = '11'
	elif m.find('Dec') != -1:
		month = '12'
	else:
		print u"月份转换错误:" + m + u"无法转换."
	return month


def weekday_transform(w):
	if w.find('Mon') != -1:
		weekday = '01'
	elif w.find('Tue') != -1:
		weekday = '02'
	elif w.find('Wed') != -1:
		weekday = '03'
	elif w.find('Thu') != -1:
		weekday = '04'
	elif w.find('Fri') != -1:
		weekday = '05'
	elif w.find('Sat') != -1:
		weekday = '06'
	elif w.find('Sun') != -1:
		weekday = '07'
	else:
		print u"星期转换错误:" + w + u"无法转换."
	return weekday


def time_write(fpath, list):
	f = open(fpath, 'w')
	for each in list:
		f.writelines(each)

		# f.writelines('\n')

	f.close()
	print "--" * 10
	print u"已写入本地文件"
	return 0


def link_report(t0, t1, content):
	time_cost = t1 - t0
	print "Link Report:"
	print u"程序运行时长:%.3f" % float(time_cost) + "s."
	error_list, content_str = content
	if error_list:
		print u"分析失败目标如下:"
		for each in error_list:
			print each.decode('utf-8').encode('gbk')
	else:
		print u"当前状态正常."
	print content_str
	print "--" * 10


def mail(mail_from, mail_password, mail_to, content, fpath_list):
	mail_server = mail_server_check(mail_from)
	if mail_server:
		msg = MIMEMultipart()
		msg['Subject'] = Header(u'双犬:[RR]好友最后登录时间', 'utf-8')
		msg['From'] = mail_from
		msg['To'] = mail_to

		text_part = MIMEText(content, 'plain', 'utf-8')
		msg.attach(text_part)

		for fpath in fpath_list:
			f = open(fpath, "rb")
			file_content = f.read()
			f.close()
			file_part = MIMEApplication(file_content)
			file_part.add_header('Content-Disposition', 'attachment', filename="result.txt")
			msg.attach(file_part)
		try:
			smtp = smtplib.SMTP(mail_server, 25)
			smtp.ehlo()
			smtp.starttls()
			smtp.ehlo()
			smtp.login(mail_from, mail_password)
			smtp.sendmail(mail_from, [mail_to], msg.as_string())
			smtp.quit()
			return u"通知/输出已放出"
		except Exception as ee:
			return u"通知放出失败:" + str(ee)


def opener_build():
	cookie = cookielib.CookieJar()
	cookieHP = urllib2.HTTPCookieProcessor(cookie)
	opener = urllib2.build_opener(cookieHP)
	return opener
	

def mail_server_check(mail_from):
	if "qq" in mail_from:			# 确认smtp服务信息
		mail_server = "smtp.qq.com"
	elif "163" in mail_from:
		mail_server = "smtp.163.com"
	elif "126" in mail_from:
		mail_server = "smtp.126.com"
	elif "gmail" in mail_from:
		mail_server = "smtp.gmail.com"
	elif "hotmail" in mail_from:
		mail_server = "smtp.live.com"
	else:
		mail_server = ""			# 其他种类邮箱待完善
	return mail_server

	
if __name__ == '__main__':
	main()
	