# -*- coding: utf-8 -*-
 
import urllib
import urllib2
import cookielib
import re
import sys
 
import config

reload(sys)
sys.setdefaultencoding('utf-8')

class Renren(object):
	def __init__(self):
		self.operate = ''  # response的对象（不含read）
		self.requestToken = self.rtk = ''
		self.icode = ''  # 验证码
		self.is_login = False

		self.cj = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		urllib2.install_opener(self.opener)
        
		self.requestToken_pattern = re.compile(r"get_check:'([-0-9]*)'")
		self.rtk_pattern = re.compile(r"get_check_x:'([a-zA-Z0-9]+)'")

		
	def login(self, email='', password='', origURL=''):
		postdata = {
			'email': email,
			'password': password,
			'origURL': origURL,
		}

		failCode_pattern = re.compile(r"&failCode=(\d+)")

		print u'正在登录……'

		while not self.is_login:
			self.operate = self._get_response(config.LOGINURL, postdata)
			cur_url = self.operate.geturl()
			web_content = self.operate.read()

			failCode = failCode_pattern.search(cur_url)
			if failCode is None:
				self.is_login = True
				print u"用户%s" % config.FAILCODE['-1']
				return True
			else:
				definate_failCode = failCode.group(1)  # 确切的failCode字符串
				print definate_failCode
				if definate_failCode in config.FAILCODE.keys():
					print config.FAILCODE[definate_failCode]
					if definate_failCode == '512':
						self._get_icode_img()
						self.icode = raw_input("请输入验证码:".decode('utf-8').encode('gb18030'))
						postdata['icode'] = self.icode
						continue
				else:
					print u'未知错误'
			return False

	def _get_response(self, url, data = None):
		if data is not None:
			req = urllib2.Request(url, urllib.urlencode(data))
		else:
			req = urllib2.Request(url)
		response = self.opener.open(req)
		return response
    
	def _get_requestToken(self, data):
		self.requestToken = self.requestToken_pattern.search(data).group(1)
		self.rtk = self.rtk_pattern.search(data).group(1)

	def _get_icode_img(self):
		icode_img = self._get_response(config.ICODEURL).read()
		self._write_file('icode.jpg', icode_img)
    
	def _write_file(self, filename, data):
		try:
			output_file = open(filename, 'wb')
			output_file.write(data)
			output_file.close()
			print u'验证码图片已写入%s' % filename
		except IOError:
			print u"验证码图片写入失败！" 