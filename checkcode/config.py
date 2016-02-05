# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
 
LOGINURL = r'http://www.renren.com/PLogin.do'
ICODEURL = r'http://icode.renren.com/getcode.do?t=login&rnd=Math.random()'
 
EMAIL = '443540221@qq.com'
PASSWORD = 'Iy5sOl2fNoo3Lvsy'

# FailCode via "login-v6.js"
FAILCODE = {
	'-1': u'登录成功',
	'0': u'登录系统错误，请稍后尝试',
	'1': u'您的用户名和密码不匹配',
	'2': u'您的用户名和密码不匹配',
	'4': u'您的用户名和密码不匹配',
	'8': u'请输入帐号，密码',
	'16': u'您的账号已停止使用',
	'32': u'帐号未激活，请激活帐号',
	'64': u'您的帐号需要解锁才能登录',
	'128': u'您的用户名和密码不匹配',
	'512': u'请您输入验证码',
	'4096': u'登录系统错误，稍后尝试',
}
