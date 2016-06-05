# -*- coding:utf-8 -*-

import urllib
import urllib2			# URL网络相关模块
import re			# 正则表达式模块
import time			# 时间相关模块
import sys			# 编码环境
import cookielib			# cookie模块
import threading			# 多线程模块
import smtplib			# 邮件发送模块
import os			# cmd命令
from email.mime.multipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.mime.application import MIMEApplication
from email.Header import Header			# 邮件正文构建模块
# from PIL import Image			# 用于验证码识别的图片模块

reload(sys)			# 重新载入sys模块
sys.setdefaultencoding("utf-8")			# 设置环境编码为utf-8,用以输出中文


def main():			# 程序主体函数
	email = raw_input('帐户名:'.decode('utf-8').encode('gbk'))			# 输入从网账户
	password = raw_input('密码:'.decode('utf-8').encode('gbk'))			# 输入从网密码
	mail_from = raw_input('邮箱发送账户:'.decode('utf-8').encode('gbk'))			# 输入发送邮箱的账户(发送至移动的139邮箱会有短信提醒)
	mail_password = raw_input('邮箱发送密码:'.decode('utf-8').encode('gbk'))			# 输入发送邮箱的密码
	mail_to = []			# 准备接收邮箱的列表
	for i in range(100):			# 接收邮箱的个数可以再提高
		mailto = raw_input('邮箱通知地址(支持QQ/163/126/hotmail/gmail)(上限100,输入0结束):'.decode('utf-8').encode('gbk'))			# 逐个输入接收邮箱的账户
		if mailto == "0":			# 输入0则认为接收邮箱已经输入完成
			break			# 退出循环
		else:			# 继续输入接收邮箱
			mail_to.append(mailto)			# 将接收邮箱添加至列表中

	date_now = time.strftime("%y%m%d", time.localtime())			# 计算当前的年月日,用以确定文件名
	shutdown_check = raw_input("程序完成后是否自动关机？输入任意内容确认关机,直接回车则不关机.".decode('utf-8').encode('gbk'))			# 确定程序运行完毕后是否自动关机
	threadnum = input('输入线程数:'.decode('utf-8').encode('gbk'))			# 输入创建的线程数量
	
	data_check(email, password, mail_from, mail_password, mail_to, shutdown_check)			# 数据确认环节,程序正式运行前最后一次退出机会
	
	print "Link Start!"			# 开始连接！
	print "--" * 10			# 分割线
	t0 = time.time()			# 计算程序开始运行的时间
	rr_opener = opener_build()			# 创建含cookie的网页打开方式

	data = login_prepare(email, password)			# 构建登录从网需要提交的数据
	loginurl = "http://3g.renren.com"			# 确定从网登录URL
	respose_read = login(loginurl, rr_opener, data)			# 确认登录，读取个人主页源码
	friend_urllist = friend_urllist_search(rr_opener, respose_read)			# 分析目标URL地址列表

	thread_init(friendpage_login, friend_urllist, rr_opener, threadnum)			# 构建多线程模型,并开始提取

	t1 = time.time()			# 计算程序结束运行的时间
	f = open(r"fr_info_error" + date_now + ".txt", 'r')			# 打开提取错误列表
	error_list = f.readlines()			# 读取错误列表内容
	f.close()			# 关闭错误列表文件
	content = "(" + str(len(friend_urllist) - len(error_list)) + "/" + str(len(friend_urllist)) + ")"			# 输出提取完成数量\样本总量
	link_report(t0, t1, content)			# 输出程序报告
	fpath = []			# 创建文件路径列表,用以邮件的附件准备
	fpath.append(r"fr_info" + date_now + ".txt")			# 导入提取输出文件
	fpath.append(r"fr_info_error" + date_now + ".txt")			# 导入错误列表文件
	mail_check = mail(mail_from, mail_password, mail_to, content, fpath)			# 发送邮件,并返回邮件发送状态
	t1 = time.time()			# 计算邮件发送结束时间
	link_report(t0, t1, mail_check)			# 输出程序报告
	print "Link Logout."			# 连接断开.
	if shutdown_check:			# 之前确认程序完成后自动关机
		os.system("shutdown.exe /s /t 30")			# 调用windows的cmd命令,在30s后自动关机
	return 0			# 主体函数结束


def login_prepare(email, password):			# 构建登录从网需要提交的数据
	ref = "http://m.renren.com/q.do?null"			# 写入访问来源
	useragent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"			# 写入本机浏览器软件信息
	postdata = {
		'email': email,
		'password': password,
		'ref': ref,
		'User-Agent': useragent
	}			# 准备数据字典
	data = urllib.urlencode(postdata)			# 对数据进行编码
	return data			# 返回将要提交的数据


def login(url, opener, data):			# 用于登录个人主页,并提取网页源码(确认登录可用)
	req = urllib2.Request(
		url,
		data
	)			# 构建打开网页请求
	respose = opener.open(req)			# 打开网页
	respose_read = respose.read()			# 读取登录个人主页的网页源码
	return respose_read			# 返回网页源码


def friend_urllist_search(opener, read):			# 构建目标基本资料网页URL列表
	f1_search = '>个人主页</a>.*?<a href="(.*?)">好友</a>'			# 个人好友列表URL的正则表达式
	f1_url = re.findall(f1_search, read, re.S)			# 提取个人好友列表URL
	req = urllib2.Request(
		f1_url[0]
	)			# 构建打开个人好友列表网页的请求
	respose = opener.open(req)			# 打开个人好友列表网页
	friendlisturl_read = respose.read()			# 读取个人好友列表页的网页源码

	f_pagenum_search = '第1/(.*?)页'			# 列表总页数的正则表达式
	f_pagenums = re.findall(f_pagenum_search, friendlisturl_read, re.S)           # 搜索共有多少页目标
	f_pagenum = int(f_pagenums[0])			# 提取最大页码

	targets = []			# 准备目标基本资料页的URL列表
	for i in range(f_pagenum):			# 对个人好友列表所有页进行遍历
		login_url = f1_url[0][:35] + "curpage=" + str(i) + f1_url[0][35:]			# 构建个人好友列表中每一页的URL地址
		req = urllib2.Request(
			login_url
		)			# 构建个人好友列表中每一页的打开请求
		respose_info = opener.open(req)			# 打开个人好友列表中的每一页
		info_read = respose_info.read()			# 读取每一页的源码
		friend_url_search = '</td><td><a href="(.*?)">.*?</a><br />'			# 目标个人主页URL的正则表达式
		friend_url = re.findall(friend_url_search, info_read, re.S)         # 获得目标个人主页URL
		for each in friend_url:			# 对当前页每个目标个人主页URL进行遍历
			targets.append(each.replace('amp;', 'htf=738&').replace('profile', 'details'))			# 构建目标基本资料网页URL
		print u"第" + str(i+1) + u"页目标网页地址采集完毕"			# 报告当前页所有目标提取完成.
	print u"已确认" + str(len(targets)) + u"个目标"			# 报告目标总数
	print "--" * 10			# 分割线
	return targets			# 返回目标基本资料网页URL列表


def friendpage_login(opener, urls, code):			# 对给定列表内所有URL进行数据提取,并写入文件
	error_target = []			# 准备错误列表
	for each in urls:			# 对给定列表内所有URL进行遍历
		req = urllib2.Request(
			each
		)			# 构建打开目标基本资料网页请求
		try:
			response = opener.open(req, timeout = 10)						# 打开目标基本资料网页,并设置最大超时为10s,超时返回错误
			response_read = response.read()			# 读取基本资料的网页源码
			response.close()			# 关闭网页
			name = name_search(response_read, each)			# 提取姓名数据
			time_str = time_search(response_read, each)			# 提取时间数据
			if time_str:			# 提取时间数据完成
				pass			# 无操作
			else:			# 提取时间数据失败
				time_str = u"未知时间"			# 将时间信息定义为未知
				error_target.append(name + "\t" + each)			# 将错误添加至错误列表中
			content = name + '\t' + time_str + '\n'			# 构建写入文件的内容
			fr_fpath = r"fr_info" + time.strftime("%y%m%d", time.localtime()) + ".txt"			# 确定数据输出文件路径
			time_write(fr_fpath, content)			# 写入内容
		except Exception:			# 基本资料页打开超时(浏览器打开时显示 系统繁忙,可能为目标用户不存在或已经注销)
			error_target.append("用户不存在或其他错误\t" + each)			# 将错误添加至错误列表中
	error_fpath = r"fr_info_error" + time.strftime("%y%m%d", time.localtime()) + ".txt"			# 确定错误立标文件路径
	error_content = "\n".join(error_target) + "\n"			# 构建错误内容
	if error_content != "\n":			# 错误列表不为空,即有错误
		time_write(error_fpath, error_content)			# 写入内容
	return 0			# 数据提取函数结束


def name_search(response_read, each):			# 提取姓名数据
	name_search = '<title>手机人人网 - (.*?)</title>'			# 姓名的正则表达式
	names = re.findall(name_search, response_read, re.S)			# 提取所有姓名数据
	name = names[0]			# 提取姓名
	try:
		print name.decode('utf-8').encode('gbk'),			# 输出姓名
	except UnicodeError as e:			# 姓名中含cmd内无法输出的字符(但可以写入文件)
		print u'姓名编码错误',			# 报告输出错误
	return name			# 返回姓名数据


def time_search(response_read, each):			# 提取时间数据
	info_search = '<b>基本信息</b></div><div.*?>(.*?)</div></div><div class="sec">'			# 基本信息的正则表达式
	infos = re.findall(info_search, response_read, re.S)			# 提取所有基本信息数据
	try:			# 部分目标基本资料页没有基本信息/基本信息为空
		info = infos[0]			# 提取基本信息

		time_search = '最后登录：(.*?)<br />'			# 时间的正则表达式
		login_time_list = []			# 时间数据存储过渡列表
		try:			# 部分目标基本资料没有时间资料
			time_infos = re.findall(time_search, info, re.S)			# 提取所有时间数据
			time_info = time_infos[0]			# 提取时间

			date_search = r'</start>(.*?) (.*?) (.*?) (.*?) (.*?) (.*?)</end>'			# 各项时间参数的正则表达式
			date_info = '</start>' + time_info + '</end>'			# 构建时间参数对象
			date = re.findall(date_search, date_info, re.S)			# 提取所有时间参数数据

			login_time_list.append(date[0][5])  # 年份信息
			login_time_list.append(month_transform(date[0][1]))  # 月份转换信息
			login_time_list.append(weekday_transform(date[0][0]))  # 星期转换信息
			login_time_list.append(date[0][2])  # 天数信息
			login_time_list.append(date[0][3])  # 具体时刻信息

			login_time = "\t".join(login_time_list)			# 根据过渡列表计算时间信息
			print u"分析完成"			# 输出本次目标的时间提取完成
			return login_time			# 返回时间
		except Exception as ee:			# 基本资料中无时间资料
			print u"登录时间分析失败,错误对象:",			# 报告时间提取错误
			print info.decode('utf-8').encode('gbk')			# 输出提取失败的对象
			return ""			# 返回空值
	except Exception as e:			# 基本信息为空
		print u"基本信息分析失败,目标URL:" + each			# 报告基本信息返回失败


def month_transform(m):			# 将英文简写月份信息转换为数字信息
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
		print u"月份转换错误:" + m + u"无法转换."			# 未知月份信息
	return month			# 返回数字月份信息


def weekday_transform(w):			# 将英文简写星期信息转换为数字信息
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
		print u"星期转换错误:" + w + u"无法转换."			# 未知星期信息
	return weekday			# 返回数字星期信息


def time_write(fpath, content):			# 按照文件路径,将内容写入文件
	if lock.acquire():			# 本线程获得文件操作权限
		f = open(fpath, 'a')			# 打开文件
		f.writelines(content)			# 写入内容
		f.close()			# 关闭文件
		lock.release()			# 释放文件操作权限
	return 0			# 文件写入函数完成


def link_report(t0, t1, content):			# 报告程序运行时间以及完成状态
	time_cost = t1 - t0			# 计算程序运行时长
	print "Link Report:"			# 准备任务报告
	print u"程序运行时长:%.3f" % float(time_cost) + "s."			# 任务运行时长报告
	if content:
		print u"程序运行状态:" + content			# 程序状态报告
	print "--" * 10			# 分割线


def mail(mail_from, mail_password, mail_to, content, fpath_list):			# 将多个文件发送至多个接收邮箱
	mail_server = mail_server_check(mail_from)			# 确定发送邮箱的smtp服务地址
	if mail_server:			# 确认发送邮箱的smtp地址
		msg = MIMEMultipart()			# 构建邮件
		msg['Subject'] = Header(u'双犬:[RR]随机用户最后登录时间', 'utf-8')			# 邮件标题
		msg['From'] = mail_from			# 邮件发送地址
		msg['To'] = ",".join(mail_to)			# 邮件接收地址

		text_part = MIMEText(content, 'plain', 'utf-8')			# 构建以content变量(完成状态)为基础的正文部分
		msg.attach(text_part)			# 将正文部分补充至邮件中

		for file_each in fpath_list:			# 对附件列表进行遍历
			f = open(file_each, "rb")			# 以二进制模式打开将作为附件的文件
			file_content = f.read()			# 读取文件内容
			f.close()			# 关闭文件
			file_part = MIMEApplication(file_content)			# 构建附件部分
			file_part.add_header('Content-Disposition', 'attachment', filename = file_each)			# 添加附件头信息,以扩展名决定对方的文件打开方式
			msg.attach(file_part)			# 将附件补充至邮件中
		try:			# 尝试发送邮件
			smtp = smtplib.SMTP(mail_server, 25)			# 以25端口构建smtp服务
			smtp.ehlo()			# 确认smtp服务
			smtp.starttls()			# 创建TLS连接
			smtp.ehlo()			# 再次确认smtp服务
			smtp.login(mail_from, mail_password)			# 登录发送邮箱
			smtp.sendmail(mail_from, mail_to, msg.as_string())			# 发送邮件
			smtp.quit()			# 注销邮箱,退出smtp服务
			return u"通知/输出已放出"			# 报告通知已经发出
		except Exception as ee:			# 邮件发送失败
			return u"对于" +each_to + u"的通知放出失败:" + str(ee)			# 报告邮件发送失败及原因


def opener_build():			# 创建cookie
	cookie = cookielib.CookieJar()			# 生成cookie实例
	cookieHP = urllib2.HTTPCookieProcessor(cookie)			# 确定cookie种类及创建方式
	opener = urllib2.build_opener(cookieHP)			# 构建模拟登录的网页打开器
	return opener			# 返回打开器


def mail_server_check(mail_from):			# 确认发送邮箱的smtp地址
	if "qq" in mail_from:  # 搜索关键字,确认smtp服务信息
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
		mail_server = ""  # 其他种类邮箱待完善
	return mail_server			# 返回stmp服务地址


def thread_init(function, mission_list, opener, threadnum):			# 根据传入的函数与目标,以及相关参数创建多线程模型
	threadpool = []			# 准备线程池
	function_list = thread_distribute(mission_list, threadnum)			# 计算各个线程的任务列表
	global lock			# 准备线程锁变量
	lock = threading.Lock()			# 创建线程锁,用以确认各个线程的文件操作权限
	threadcode = 0			# 线程码
	for i in range(0, threadnum):			# 对各个需要创建的线程进行遍历
		threadcode += 1			# 线程码变更
		t = threading.Thread(target=function, args=[opener, function_list[i], threadcode])			# 创建线程
		threadpool.append(t)			# 将创建的线程填入线程池
	for t in threadpool:			# 对多线程进行遍历
		t.start()			# 开始各个线程
	for t in threadpool:			# 对多线程进行遍历
		t.join()			# 确认各个线程均已运行完成
	return 0			# 多线程模型运行完成


def thread_distribute(mission_list, threadnum):			# 按照任务列表与线程数量分配任务
	function_list = [[] for i in range(0, threadnum)]			# 创建包含各个线程任务列表的线程列表
	for i in range(0, len(mission_list)):			# 对任务列表进行遍历,将任务轮流分配至各个线程
		index = i % threadnum			# 计算当前线程
		function_list[index].append(mission_list[i])			# 将此任务添加至当前线程的任务列表中
	return function_list			# 返回分配结果


def data_check(email, password, mail_from, mail_password, mail_to, shutdown_check, **kw):			# 输出各项准备数据,用以确认
	print "**" * 10			# 大分割线
	print "Link Check:"			# 报告程序确认
	print "--" * 10			# 分割线
	print u"从网账户:" + email			# 确认从网账户密码
	print u"从网密码:" + password
	print "--" * 10			# 分割线
	print u"邮箱账户:" + mail_from			# 确认发送邮箱账户密码
	print u"邮箱密码:" + mail_password
	print "--" * 10			# 分割线
	print u"通知地址:"			# 确认接收邮箱列表
	for each in mail_to:			# 对接收邮箱列表进行遍历
		print each + ",",			# 确认各个接收邮箱
	print ""			# 换行
	print "--" * 10			# 分割线
	if shutdown_check:			# 确认程序运行完成后自动关机
		print u"运行完成后自动关机"
	else:
		print u"运行完成后不关机"
	print "--" * 10			# 分割线
	for key in kw.keys():			# 对其他信息进行确认
		if key == "init":			# 确认样本起点
			print u"样本起点",
			print ":",
			print kw[key]
		elif key == "final":			# 确认样本终点
			print u"样本终点",
			print ":",
			print kw[key]
		elif key == "ranger":			# 确认样本数量
			print u"样本数量",
			print ":",
			print kw[key]
	check = raw_input("确认无误后输入0,回车运行程序.输入其他内容程序结束:".decode('utf-8').encode('gbk'))			# 等待用户确认信息
	if check == "0":			# 所有数据无误
		print u"数据确认完成,程序即将启动."			# 报告程序启动
		print "**" * 10			# 大分割线
	else:
		print u"数据确认失败,程序即将结束."			# 报告程序退出
		print "**" * 10			# 大分割线
		exit()			# 退出程序
	return 0			# 数据确认函数完成
	
	
if __name__ == '__main__':
	main()			# 程序启动
	