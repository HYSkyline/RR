# -*- coding: utf-8 -*-

import sys

import config
import renren_check

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == "__main__":
	my_account = renren_check.Renren()
	my_account.login(config.EMAIL, config.PASSWORD, '')