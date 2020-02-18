"""
 the class ConcurrentHander  is used to get the lastest secode-house information of lianjia.
"""
import urllib.parse
import ssl
from urllib import request
import hashlib
import json
from http import cookiejar
import sys
from bs4 import BeautifulSoup
import concurrent.futures
import queue
import time

class ConcurrentHander :
    '''
    gets the lastest seconde-hand house information  of lianjia from the website(https://xa.lianjia.com/ershoufang/)
    '''
    def __init__(self,exe_path,house_name,debug,config,log):

        self.exe_path=exe_path
        self.config=config
        self.house_name=house_name
        self.house_page_url_queue=queue.Queue()
        self.house_page_content_queue=queue.Queue()
        self.detail_url_queue= queue.Queue()

        self.detail_page_queue=queue.Queue()
        self.house_detail_info_queue=queue.Queue()

        self.house_total_num=0
        self.cookie_file=self.exe_path+'/file/cookie'
        self.cookie=cookiejar.MozillaCookieJar(self.cookie_file)
        self.hander=request.HTTPCookieProcessor(self.cookie)
        self.opener=request.build_opener(self.hander,urllib.request.HTTPHandler(debuglevel=debug))
        self.http_header={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103     Safari/537.36",
        "Cookie": " userId=7; type=0; username=huayang; remember=false; password=e10adc3949ba59abbe56e057f20f883e",
        "Referer": "http://www.guozdx.com/"
        }
        self.timeout=5
        self.log=log

    def clear(self):
        self.house_page_url_queue=queue.Queue()
        self.house_page_content_queue=queue.Queue()
        self.detail_url_queue= queue.Queue()
        self.detail_page_queue=queue.Queue()
        self.house_detail_info_queue=queue.Queue()
    
    def __extract_house_total_num__(self,page):
        data_json=json.loads(page)
        if type(data_json)==dict:
            if 'data' in data_json:
                if 'info' in data_json['data']:
                    if 'sellNum' in data_json['data']['info']:
                        self.house_total_num=int(data_json['data']['info']['sellNum'])
                        
    def get_house_total_num(self):
        url='https://xa.lianjia.com/api/listtop?semParams%5BsemResblockId%5D=3820031038702754&semParams%5BsemType%5D=resblock&semParams%5BsemSource%5D=ershou_xiaoqu'
        page=self.request_page(url)
        self.__extract_house_total_num__(page)


    def request_page(self,url):
        '''
        request the url 
        '''
        request = urllib.request.Request(url,headers=self.http_header)
        try:
            response = self.opener.open(request,timeout=self.timeout)

        except Exception as e:
            self.log.debug('except: {0}'.format(e))
            self.log.debug('request {0} failure!'.format(url))
            return ''
        except:
            self.log.debug('unkown except')
            return ''
        if response.code==200:
            html = response.read().decode("utf-8")

        return html  
 
    def __get_house_detail_page__(self,id):
        '''
        log on the site firstly. then save the cookie that site send .
        '''
        i=0
        while True:
            data=self.detail_url_queue.get()
            url=data[1]
            i=i+1
            self.detail_url_queue.task_done()
            self.log.debug('thread:{0} request:{1}'.format(id,url))

            html=self.request_page(url)
            if len(html)!=0:
                self.detail_page_queue.put((data[0],html))
            else:
                return False
            if self.detail_url_queue.empty():
                break;
            
            #print(html)
        
        self.log.debug('get house detail page thread{}:executor {} task'.format(id,i))
        return True

    def concurrent_get_house_detail_page(self):
        start=time.time()
        thread_num=self.config.get('thread','get_house_detail_page_thread_num')
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(thread_num)) as executor:
           
            future_to_url = {executor.submit(self.__get_house_detail_page__,id): id for id in range(0,int(thread_num))}
            for future in concurrent.futures.as_completed(future_to_url):
                id = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    self.log.debug('%r generated an exception: %s' % (id, exc))
                    
                else:
                    if not data:
                        return False
                    self.log.debug('get house detail page thread:{} is done'.format(id))
        size=self.detail_page_queue.qsize()  
        if size==0:
            return False 
        self.detail_url_queue.join()
        self.log.info('总共下载{}个房屋详情页'.format(size))
        end=time.time()
        total_time=end-start
        self.log.info('get house detail page :{}'.format(total_time))
        return True

    def __extract_house_detail__(self,id):
        '''
        extract all house information from every detail url and save it to house_detail_info_list
        '''
        i=0
        while True :
            data=self.detail_page_queue.get()
            page=data[1]
            i=i+1
            self.detail_page_queue.task_done()
            house_detail=HouseDetail()
            house_detail.house_id=data[0]
            soup=BeautifulSoup(page,'lxml')
            for div in soup.find(class_="overview").children:
                if div['class'][0]=='content':
                    for item in div.children:
                        
                        if item['class'][0]=='price':
                            for span in item.children:
                                if span['class'][0]=='total':
                                    house_detail.total_price=span.string
                                if span['class'][0]=='text':
                                    for div in span.children:
                                        if div['class'][0]=='unitPrice':
                                            for span  in div.children:
                                                if span['class'][0]=='unitPriceValue':
                                                    for str in span.strings:
                                                        house_detail.average_price=str
                                                        break;
                        if item['class'][0]=='houseInfo':
                            for div in item.children:
                                if div['class'][0]=='area':
                                    for div2 in div.children:
                                        if div2['class'][0]=='mainInfo':
                                            house_detail.area=div2.string
                                if div['class'][0]=='room':
                                    for div2 in div.children:
                                        if div2['class'][0]=='mainInfo':
                                            house_detail.layout=div2.string
                                if div['class'][0]=='type':
                                    for div2 in div.children:
                                        if div2['class'][0]=='subInfo':
                                            house_detail.dress=div2.string                       
                                        if div2['class'][0]=='mainInfo':
                                            house_detail.tongtou=div2.string 
            self.house_detail_info_queue.put(house_detail)
            if self.detail_page_queue.empty():
                break;

        self.log.debug('extract house detail thread{}:executor {} task'.format(id,i))

    def concurrent_extract_house_detail(self):
        start=time.time()
        thread_num=self.config.get('thread','extract_house_detail_thread_num')
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(thread_num)) as executor:
           
            future_to_url = {executor.submit(self.__extract_house_detail__,id): id for id in range(0,int(thread_num))}
            for future in concurrent.futures.as_completed(future_to_url):
                id = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    self.log.debug('%r generated an exception: %s' % (id, exc))
                else:
                    self.log.debug('extract house detail thread:{} is done'.format(id))
        self.detail_page_queue.join()
        self.log.info('总共提取{}个房屋详细信息'.format(self.house_detail_info_queue.qsize()))
        end=time.time()
        total_time=end-start
        self.log.info('extract house detail :{}'.format(total_time))

    def __extract_house_url__(self,soup):
        '''
        extract all href of house page from tag of bigImgList 
        '''
        for div in soup.find(class_="bigImgList").children:
            if div['class'][0]=='item':
                house_id=div['data-houseid']
            for img in div.children:
                if img['class'][0]=='img':
                    self.detail_url_queue.put((house_id,img['href']))
                    
        
    def __extract_house_info__(self,id):
        '''
        extract all href of house page and save it to house_detail_info_url
        '''

        i=0
        while True:
            page=self.house_page_content_queue.get()
            i=i+1
            self.house_page_content_queue.task_done()
            soup=BeautifulSoup(page,'lxml')
            try:
                self.__extract_house_url__(soup)
            except:
                print('unknown except')
                return False
            if self.house_page_content_queue.empty():
                break;

        self.log.debug('extract house url thread{}: executor {} task done'.format(id,i))
        return True

    def concurrent_extract_house_info(self):
        '''
        extract the url of each house from the house page
        '''
        
        start=time.time()
        thread_num=self.config.get('thread','extract_house_info_thread_num')

        with concurrent.futures.ThreadPoolExecutor(max_workers=int(thread_num)) as executor:
        
           future_to_url = {executor.submit(self.__extract_house_info__,id): id for id in range(0,int(thread_num))}
           
           for future in concurrent.futures.as_completed(future_to_url):
                id = future_to_url[future]
                try:
                    ret = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (id, exc))
                    return False
                else:
                    if not ret:
                        return ret       
        self.house_page_content_queue.join()
        self.log.info('总共提取{}个房屋url'.format(self.detail_url_queue.qsize()))
        end=time.time()
        total_time=end-start
        self.log.info('extract house url :{}'.format(total_time))


    def __request_page__(self,url):
        '''
        request the url by given
        '''
        request = urllib.request.Request(url,headers=self.http_header)
        try:
            response = self.opener.open(request,timeout=self.timeout)

        except urllib.error.URLError as e:
            self.log.debug('except: {0}'.format(e.reason))
            self.log.debug('request {} failure!'.format(url))
            return ''
        else:
            if response.code==200:
                html = response.read().decode("utf-8")
            return html   
   
    def __get_house_page_info__(self,id):
        '''
        request the house page of lianjia
        '''
      
        i=0
        while True:
            url=self.house_page_url_queue.get()
            i=i+1
            self.house_page_url_queue.task_done()
            html=self.request_page(url)
            if len(html)!=0:
                self.house_page_content_queue.put(html)
            else:
                return False
            if self.house_page_url_queue.empty():
                break;

        self.log.debug('get house page thread{}: executor {} task done'.format(id,i))
        return True

    def concurrent_get_house_page_info(self):
        '''
        concurrently request every page  that you want to search from lianjia
        '''
        start=time.time()   
        urlencode_house_name=urllib.parse.quote(self.house_name)
        url='https://xa.lianjia.com/ershoufang/pg{}rs'+urlencode_house_name+'/'

        num_page_per=int(self.config.get('page','num_page_per'))
        page_total_num=self.house_total_num/num_page_per
        page_total_num_int=self.house_total_num//num_page_per

        if page_total_num>page_total_num_int:
            page_total_num=page_total_num_int+1

        print(page_total_num)
        for page in range(1,page_total_num+1):
            url2=url.format(page)
            self.house_page_url_queue.put(url2)
        thread_num=self.config.get('thread','get_house_page_thread_num')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(thread_num)) as executor:
           
            future_to_url = {executor.submit(self.__get_house_page_info__,id): id for id in range(0,int(thread_num))}
            for future in concurrent.futures.as_completed(future_to_url):
                id = future_to_url[future]
                try:
                    ret = future.result()
                except Exception as exc:
                    self.log.debug('%r generated an exception: %s' % (id, exc))
                    return False
                else:
                    if not ret:
                        return ret
        self.house_page_url_queue.join()
        size=self.house_page_content_queue.qsize()
        self.log.info('总共{}个页面'.format(size))
        if size==0:
            return False
        end=time.time()
        total_time=end-start
        self.log.info('get house page :{}'.format(total_time))
        return True


class HouseDetail:

    def __init__(self):
        self.house_id=''
        self.total_price=''
        self.average_price=''
        self.area=''
        self.layout=''
        self.dress=''
        self.tongtou=''
    def to_string(self):
        return [self.house_id,self.total_price,self.average_price,self.area,self.layout,self.dress,self.tongtou]
   


