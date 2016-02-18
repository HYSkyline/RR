# -*- coding:utf-8 -*-

import urllib
import urllib2
import cookielib
import re
import time
import sys
from PIL import Image
import smtplib
from email.mime.text import MIMEText

reload(sys)			# 重新载入sys模块
sys.setdefaultencoding('utf-8')			# 环境编码由ascii变为utf-8

class RR_rp():			# 创建对应人人账号类，包含帐户名、密码、人品列表等属性
	def __init__(self, username, password, mail_from, mail_password):			# 初始化函数
		self.email = username			# 确认帐户名信息
		self.password = password			# 确认密码信息
		self.domain = 'renren.com'			# 确认登录来源信息
		self.checkcode = ''
		self.loginurl = 'http://www.renren.com/PLogin.do'			# 确认登录网页
		self.login_check = False
		
		self.mail_from = mail_from			# 确认通知发起方信息
		self.mail_password = mail_password			# 确认通知发起方密码
		self.mail_to = "15861811808@139.com"			# 确认通知发送目标
		if "qq" in self.mail_from:			# 确认smtp服务信息
			self.mail_server = "smtp.qq.com"
		elif "163" in self.mail_from:
			self.mail_server = "smtp.163.com"
		elif "126" in self.mail_from:
			self.mail_server = "smtp.126.com"
		elif "gmail" in self.mail_from:
			self.mail_server = "smtp.gmail.com"
		elif "hotmail" in self.mail_from:
			self.mail_server = "smtp.live.com"
		else:
			print u"未知邮箱"			# 其他种类邮箱待完善
			exit()			# 退出程序
		self.mail_check = False			# 邮件发送确认变量默认为未发送(false为未发送,true为已发送)
	
	
	def main(self):			# 主体程序
		print "Link Start!"			# 开始连接！
		print "--" * 10			# 分行符
		t0 = time.time()			# 确认程序开始的时间，准备计算程序运行时长
		self.rr_opener = self.cookie_build()
		response_read = self.login(url=self.loginurl)				# 读取网页源码(可能遭遇验证码拦截)
		
		renpin_url_search = 'target="_blank"></a><a href="(.*?)" target="_blank" class="for_content">'			# RP网页URL的正则表达式
		renpin_list_search = '</a><div class="name"><a target="_blank" href="http://www.renren.com/.*?">(.*?)</a></div><div class="score">(.*?)</div></li>'			# RP列表的正则表达式
		
		try:
			renpin_url = self.re_search(renpin_url_search, response_read)			# 搜索RP网页的URL	
			RP_response_read = self.rr_opener.open(renpin_url[0]).read()			# 读取RP网页源码
			try:
				renpin_list = self.re_search(renpin_list_search, RP_response_read)			# 搜索RP信息
				self.rp_write(renpin_list)			# 将RP信息写入本地文件
				content = self.list_transform(renpin_list)			# 将RP列表转变为字符串变量
				mail_check = self.mail(content)			# 将RP信息通知至目标
				self.link_report(t0, renpin_list)
			except Exception as ee:
				print u"RP值读取失败:" + str(ee)			# RP网页读取失败
		except Exception as e:			# 个人主页登录失败
			print u"网页读取错误" + str(e)			# 输出网页登录问题
		
		print "Link Logout."
	
	def login(self, url):			# 登录个人主页
		self.code_checkin()
		self.icode = ""
		print u'验证码确认:' + str(self.checkcode)
		postdata = {
			'email': self.email,
			'password': self.password,
			'domain': self.domain,
			'icode': str(self.checkcode)
		}			# 准备需要提交的数据
		data = urllib.urlencode(postdata)			# 对提交数据进行编码
		req = urllib2.Request(
			url,
			data
		)			# 构建网页登录请求
		response = self.rr_opener.open(req)			# 打开网页
		response_geturl = response.geturl()
		failcode_list = re.findall(r'&failCode=(\d+)', response_geturl)
		if failcode_list:
			failcode = failcode_list[0]
			if failcode in ['1', '2', '4']:
				print u"账户/密码错误"
				exit()
			elif failcode == '16':
				print u"账号已禁用"
				exit()
			elif failcode == '32':
				print u"账户无效"
				exit()
			elif failcode == '64':
				print u"账号已锁定"
				exit()
			elif failcode == '512':
				print u"验证码错误"
				exit()
			elif failcode in ['0', '4096']:
				print u"系统错误，稍后重试"
				exit()
		else:
			print u"登录完成"
			print "--" * 10
			self.login_check = True
			read = response.read()			# 分析网页源码
		return read			# 返回源码
		
	
	def cookie_build(self):			# 建立cookie信息
		cookie = cookielib.CookieJar()			# 生成CookieJar实例
		cookie_Hp = urllib2.HTTPCookieProcessor(cookie)			# 未知
		opener = urllib2.build_opener(cookie_Hp)			# 根据cookie_Hp构建打开模式
		urllib2.install_opener(opener)
		return opener			# 返回登录器
		
	
	def code_checkin(self):			# 调用浏览器显示验证码图片，并提交验证码信息
		code_check_url = 'http://icode.renren.com/getcode.do?t=web_login&rnd=Math.random()'			# 验证码的网页URL
		code_response = urllib2.urlopen(code_check_url)			# 打开验证码网页
		code_response_read = code_response.read()			# 读取验证码图片
		fpath = r'F:\application\python\RR\code_check.jpg'			# 确认验证码图片存储位置
		f = open(fpath, 'wb')			# 以二进制写入模式创建jpg文件
		f.write(code_response_read)			# 写入验证码图片信息
		f.close()			# 写入完成，关闭文件
		code_image = Image.open(fpath)			# 调用Image模块中的图片模式打开文件
		code_image.show()			# 调用系统默认的jpg浏览器查看图片
		self.checkcode = raw_input('验证码:'.decode('utf-8').encode('gbk'))			# 提示输入验证码
		
		
	def re_search(self, search, response_read):			# 通过正则表达式进行检索
		re_list = re.findall(search, response_read, re.S)			# 正则搜索
		return re_list			# 返回搜索结果列表
	
	
	def rp_write(self, renpin_list):			# 写入本地文件
		time_now=time.strftime('%Y%m%d',time.localtime(time.time()))			# 获取现在的日期
		minutes_now = time.strftime('%H:%M:%S',time.localtime(time.time()))			# 获取现在的时刻
		fpath = r"F:\application\python\RR\rr_rp_result.txt"			# 输入文件保存信息
		f=open(fpath, 'a')			# 以追加模式打开文件，准备输入今天的信息
		for each in renpin_list:			#按人品列表中的各项数据进行循环
			try:
				f.writelines((each[0].decode('utf-8'))+"\tscore:\t"+str(each[1])+ "\t" + str(minutes_now) + "\t" + str(time_now))			# 写入各项数据(列表为二维，第一维为人名，第二维为人品值)
				f.writelines('\n')			# writelines没有自动换行功能，因此手动写入换行符
			except Exception as eee:
				print str(eee)
		f.close()			# 关闭文件，程序执行完成
	
	
	def list_transform(self, renpin_list):			# 将RP列表转变为字符串变量
		contents = []			# 过程列表变量
		for each in renpin_list:			# each为二维列表
			contents.append(':'.join(each))			# each转为字符串，存入过程列表变量当中
		content = '\n'.join(contents)			# 过程变量转为目标字符串
		return content			# 返回字符串变量
		
	
	def mail(self, content):			# 将content信息发送至目标位置
		msg = MIMEText(content, "plain", "utf-8")			# 构建邮件内容
		msg['Subject'] = u"Python:[RR]人品值日常输出"			
		msg['From'] = self.mail_from			# 构建邮件发送人
		msg['to'] = self.mail_to			# 构建邮件收信人
		try:
			smtp = smtplib.SMTP(self.mail_server, 25)			# 以25端口构建smtp邮件发送服务
			smtp.ehlo()
			smtp.starttls()			# 确认邮件发送采取TLS模式
			smtp.ehlo()
			# smtp.set_debuglevel(1)			# 显示邮件发送调试信息
			smtp.login(self.mail_from, self.mail_password)			# 登录邮箱服务
			smtp.sendmail(self.mail_from, [self.mail_to], msg.as_string())			# 发送邮件
			smtp.quit()			# 断开邮件连接
			self.mail_check = True			# 确认邮件已发送
		except Exception as e:			# 邮件发送错误
			print u"邮件发送失败" + str(e)
		
		
	def link_report(self, t0, renpin_list):			# 任务报告
		t1 = time.time()			# 确认程序运行结尾的时间
		self.time_cost = t1 - t0			# 计算程序运行时长
		print "Link Report:"			# 开始任务报告
		for each in renpin_list:			# 输出RP列表信息
			try:
				print each[0].decode('utf-8') + '\t' + 'score:' + each[1] + '\tdetected.'
			except UnicodeEncodeError as eee:			# 目标ID中包含复杂字符
				try:
					print each[0][:9].decode('utf-8') + '\t' + 'score:' + each[1] + '\tdetected.'
				except UnicodeEncodeError as eeee:
					try:
						print each[0][:6].decode('utf-8') + '\t' + 'score:' + each[1] + '\tdetected.'
					except UnicodeEncodeError as eeeee:
						print u"字符无法在cmd环境下输出(已写入txt文件)"
		print u"程序运行时长:%.3f" % float(self.time_cost) + "s."			# 输出程序运行时长
		if self.mail_check:			# 报告通知是否发出
			print u"通知已发出."
		print "--" * 10
	
	
if __name__ == '__main__':
	username = raw_input('用户名:'.decode('utf-8').encode('gbk'))			# 输入从网账户
	password = raw_input('密码:'.decode('utf-8').encode('gbk'))			# 输入从网密码
	mail_from = raw_input('邮箱(仅支持QQ、163、126、Gmail邮箱)'.decode('utf-8').encode('gbk'))			# 输入通知发起账户
	mail_password = raw_input('邮箱密码'.decode('utf-8').encode('gbk'))			# 通知通知发起密码

	rr_rp = RR_rp(username, password, mail_from, mail_password)			# 构建从网账户对象
	rr_rp.main()			# 调用程序主体
