#！/usr/bin/env python3
# -*- coding: utf-8 -*-
from selenium import webdriver
driver = webdriver.PhantomJS(executable_path='D:/phantomjs/bin/phantomjs.exe')
url0='http://www.medtiku.com/api/ques.php?cid=832'
#url='http://59.231.9.142:32004/dzjc/#/f/dzjc_ruleEngine/SuperviseInfoInstanceList'
driver.get(url0)
txt=driver.page_source 
driver.quit()
print(txt)
if __name__=='__main__':
    pass