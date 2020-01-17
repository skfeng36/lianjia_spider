"""
 cookie expires at some hours later when we log on site,
 so we need  take the  cookie that log on site  to request  site  every times 
"""
import urllib.parse
import ssl
from urllib import request
import hashlib
import json
from http import cookiejar
import sys
from bs4 import BeautifulSoup
class HouseInfo :
    '''
    gets the lastest seconde-house information  of lianjia from the website(https://xa.lianjia.com/ershoufang/)
    '''
    def __init__(self,exe_path,house_name,debug=1):

        self.exe_path=exe_path
        self.html_file_name=self.exe_path+'/html'
        self.cookie_file=self.exe_path+'/file/cookie'
        self.cookie=cookiejar.MozillaCookieJar(self.cookie_file)
        self.hander=request.HTTPCookieProcessor(self.cookie)
        self.opener=request.build_opener(self.hander,urllib.request.HTTPHandler(debuglevel=debug))
        self.house_name=house_name
        self.house_page_content_list=[]
        self.house_detail_info_url=[]
        self.http_header={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103     Safari/537.36",
        "Cookie": " userId=7; type=0; username=huayang; remember=false; password=e10adc3949ba59abbe56e057f20f883e",
        "Referer": "http://www.guozdx.com/"
        }
        self.house_detail_page_list=[]
        
    def request_page(self,url):
        request = urllib.request.Request(url,headers=self.http_header)
        try:
            response = self.opener.open(request)

        except urllib.error.URLError as e:
            print('except: {0}'.format(e.reason))
            print('request  https://xa.lianjia.com/ershoufang failure!')
            return False
        if response.code==200:
            html = response.read().decode("utf-8")
        return html   
   
    def get_house_page_info(self):
        '''
        log on the site firstly. then save the cookie that site send .
        '''
      
        urlencode_house_name=urllib.parse.quote(self.house_name)
        url='https://xa.lianjia.com/ershoufang/pg{}rs'+urlencode_house_name+'/'
        for page in range(1,2):
            url2=url.format(page)
            html=self.request_page(url2)
            if len(html)!=0:
                self.house_page_content_list.append(html)
            #print(html)
        return True
    
    def get_house_detail_page(self):
        '''
        log on the site firstly. then save the cookie that site send .
        '''

        for url in self.house_detail_info_url:
            html=self.request_page(url)
            if len(html)!=0:
                self.house_detail_page_list.append(html)
            #print(html)
        print(len(self.house_detail_page_list))
        return True





