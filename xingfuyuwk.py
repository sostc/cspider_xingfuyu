import requests
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, UnexpectedAlertPresentException
from selenium.webdriver.common.keys import Keys
import random
import time
import re

class User(object):
    def __init__(self,uname,passwd):
        self.uname = uname
        self.passwd = passwd
        self.driver = None
        self.cookie = None
        
    def comment(self,url,content):
        if not self.cookie:
            if not self.login():
                print('can not login')
                return None
        res = self._comment(url,content).json()
        if res['code'] == 100:
            print(url+"\t评论成功\t用户："+self.uname+"\t内容："+content)
            return 1
        else:
            print(url+"\t评论失败\t用户："+self.uname+"\t内容："+content)
            print(res)
            return 0
    
    def _comment(self, comment_url, content):
        d = re.findall(r"/\d+_\d+_\d+/", comment_url)[0][1:]
        newcode, tid, _ = d.split("_")
        url = "https://xingfuyuwk.fang.com/house/ajaxrequest/dianpingReplyAdd.php"
        headers = {
            "referer": "https://xingfuyuwk.fang.com/dianping/2812153868_6984062_48999770/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        }
        data = {
            "tid": tid,
            "content": content,
            "city": "广州",
            "newcode": newcode
        }
        jar = requests.cookies.RequestsCookieJar()
        for i in self.cookie:
            jar.set(i['name'], i['value'])
        response = requests.post(
            url, headers=headers, data=data, cookies=jar)
        return response
    
    
    def login(self):
        option = webdriver.ChromeOptions()
        option.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=option)
        login_url = "https://passport.fang.com/"
        self.driver.get(login_url)
        self.driver.find_element_by_class_name(
            "login-cont").find_element_by_css_selector("span:nth-child(2)").click()
        self.driver.find_element_by_id("username").send_keys(self.uname)  # 账号
        self.driver.find_element_by_id("password").send_keys(self.passwd)      # 密码
        self.driver.find_element_by_id("loginWithPswd").click()
        time.sleep(3)
        try:
            alert = self.driver.switch_to_alert()
            alert.accept()
        except NoAlertPresentException:
            pass
        cookies = self.driver.get_cookies()
        self.cookie = cookies
        return 1
    
    def like(self, comment_url):
        self.driver.get(comment_url)
        self.driver.find_element_by_id("pclpdpdetai_A03_04").click()
        time.sleep(2)
        try:
            alert = self.driver.switch_to_alert()
            alert.accept()
        except NoAlertPresentException:
            pass
        time.sleep(2)
        self.driver.quit()
        print(comment_url+"\t点赞成功\t"+self.uname)
        return 1
    
class Robot(object):
    def __init__(self):
        self.time_inverval = config['time_inverval']
        self.user_list =[User(uname,passwd) for uname,passwd in config['users']]
        self.comment_list = [Comment(comment_url) for comment_url in config['comment_url'] ]
        
    def run(self):
        to_comment = [c for c in self.comment_list if c.count<50]
        while len(to_comment)>0:
            for url in to_comment:
                for user in self.user_list:
                    if user.comment(url.comment_url,random.choice(url.content_list)):
                        if not url.like:
                            user.like(url.comment_url)
                            url.like = True
                        time.sleep(self.time_inverval)
                        url.count += 1
                    else:
                        url.count = 50
                    
            to_comment = [c for c in self.comment_list if c.count<50]
#             print(to_comment)
                
                
class Comment(object):
    def __init__(self,comment_url):
        self.comment_url = comment_url
        self.count = 0
        self.like = False
        self.content_list = [comment_content for comment_content in config['comment_content']]


if __name__ == "__main__":
    config = {}
    
    base_path = "./data"
    user_path = base_path + "/user.txt"
    comment_url_path = base_path + "/comment_url.txt"
    comment_content_path = base_path + "/comment_content.txt"
    time_inverval_path = base_path + "/time.txt"

    config['time_inverval'] = int(open(time_inverval_path).readline())
    config['users'] = [tuple(i.strip().split(':')) for i in open(user_path)]
    config["comment_url"] = [url.strip() for url in open(comment_url_path)]
    config["comment_content"] = [content.strip() for content in open(comment_content_path,encoding='utf-8')]

    robot = Robot()
    robot.run()
