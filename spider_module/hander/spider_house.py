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
import csv
import os
import threading

from http.server import HTTPServer,BaseHTTPRequestHandler
class ConcurrentHander :
    '''
    gets the lastest seconde-hand house information  of lianjia from the website(https://xa.lianjia.com/ershoufang/)
    '''
    def __init__(self,root_url,debug,config,log):

        self.debug=debug
        self.log=log
        self.config=config
        self.exe_path=self.config.get('file','exe_path')
        self.root_flie_dir=self.config.get('dir','root_file_dir')
        self.root_url=root_url
        self.region_url_queue=queue.Queue()
        self.region_expand_url_queue=queue.Queue()
        self.region_expand_url_list=[]

        self.region_page_content_queue=queue.Queue()
        self.region_page_content_list=[]

        self.house_url_queue= queue.Queue()

        self.house_url_list=[]

        self.house_url_detail_page_queue=queue.Queue()

        self.house_url_detail_page_list=[]

        self.house_detail_info_queue=queue.Queue()

        self.prefix_url='https://xa.lianjia.com'

        self.num_page_per=int(self.config.get('page','num_page_per'))
        self.save_detail_page_num=0
        self.download_detail_page_num=0


        self.house_total_num=0
        self.cookie_file=self.exe_path+'/file/cookie'
        self.cookie=cookiejar.MozillaCookieJar(self.cookie_file)
        self.hander=request.HTTPCookieProcessor(self.cookie)
        self.opener=request.build_opener(self.hander,urllib.request.HTTPHandler(debuglevel=debug))
        self.http_header={
        "User-Agent": "Baiduspider",
        "Cookie": " userId=7; type=0; username=huayang; remember=false; password=e10adc3949ba59abbe56e057f20f883e",
        "Referer": "http://www.guozdx.com/"
        }
        self.timeout=5
        self.log=log
     
    def save_detail_page(self):
        consumer=ConsumerDetailPageThread('consumer_detail_page_thread',self.house_url_detail_page_queue,self.root_url,self.debug,self.config,self.log)
        consumer.start()



    def __get_house_detail_page__(self,id):
        '''
        log on the site firstly. then save the cookie that site send .
        '''
        i=0
        n=1
        while True:
            
            data=self.house_url_queue.get()
            url=data.href
            i=i+1
            self.house_url_queue.task_done()
            self.log.debug('thread:{0} request:{1}'.format(id,url))
 
            if i<1000*n:
                time.sleep(n)
            else:
                n=n+1
            
            html=self.__request_page__(url)
            if len(html)!=0:
                data.house_detail_page=html
                #self.house_url_detail_page_list.append(data)
                self.house_url_detail_page_queue.put(data)
                self.download_detail_page_num=self.download_detail_page_num+1
            else:
                self.house_url_queue.put(data)
                print('house_url_queue put {0}'.format(data.href))
                
            if self.house_url_queue.empty():
                break;
            
            #print(html)
        
        self.log.debug('get house detail page thread{}:executor {} task'.format(id,i))
        return True

    def get_house_url_detail_page(self):
        start=time.time()
        thread_num=int(self.config.get('thread','get_house_detail_page_thread_num'))

        num=self.house_url_queue.qsize()
        if num<thread_num:
            thread_num=num
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
           
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
    
        self.house_url_queue.join()
        self.log.info('总共下载{}个房屋详情页'.format(self.download_detail_page_num))
        '''
        file_name=self.root_flie_dir+'/file/city/xian/region/'+self.house_url_detail_page_list[0].region+'/url_detail_page'
    
        self.__mkdir___(file_name)
        
    
        self.__save_house_url_detail_page__(file_name)
        '''
        end=time.time()
        total_time=end-start
        self.log.info('get_house_url_detail_page :{}'.format(total_time))
        return True

    def __save_house_url_detail_page__(self,file_name):
    
        for data in self.house_url_detail_page_list:
            name=file_name+'/'+data.house_id+'.html'
        
            self.__save_file_page__(name,data.house_detail_page)


    def __extract_house_url__(self,soup,region):
        '''
        extract all href of house page from tag of bigImgList 
        '''
        house_info_list={}
        for div in soup.find(class_="bigImgList").children:
            if div['class'][0]=='item':
                house_id=div['data-houseid']
                
            for img in div.children:
                if img['class'][0]=='img':
                    house_info=HouseInfo()
                    house_info.region=region
                    house_info.href=img['href']
                    house_info.house_id=house_id
                    self.house_url_queue.put(house_info)
                    data=[]
                    data.append(house_id)
                    data.append(house_info.href)
                    data.append(house_info.region)
                    self.house_url_list.append(data)
                    
            house_info_list[house_id]=house_info

        
        for div in soup.find(class_="sellListContent").children:
            if div['class'][0]=='clear':
                if div['data-lj_action_housedel_id'] in house_info_list:
                    house_info=house_info_list[div['data-lj_action_housedel_id']]
                    house_info.neighborhood_id=div['data-lj_action_resblock_id']
                
            for clear in div.children:
                
                if clear['class'][0]=='info':
                    for follow in clear.children:
                        if follow['class'][0]=='followInfo':
                            
                            for data in follow.strings:
                                content=data.split('/')
                                house_info.publish_time=content[1]
                                house_info.focus_num=content[0]
                                
                            
    def __extract_house_info__task__(self,id):
        '''
        extract all href of house page and save it to house_detail_info_url
        '''

        i=0
        while True:
            data=self.region_page_content_queue.get()
            i=i+1
            self.region_page_content_queue.task_done()
            #print('extract_house_url:{0}'.format(data[1]))
            
            soup=BeautifulSoup(data[1],'lxml')
            
            try:
                self.__extract_house_url__(soup,data[0])
            
            except Exception as ex:
                print('unknown except:{0}'.format(ex))
                return False
            if self.region_page_content_queue.empty():
                break;

        self.log.debug('extract house url thread{}: executor {} task done'.format(id,i))
        return True

    def extract_house_url_info(self):
        '''
        extract the url of each house from the house page
        '''
        
        start=time.time()
        thread_num=int(self.config.get('thread','extract_house_info_thread_num'))
        num=self.region_page_content_queue.qsize()
        if num<thread_num:
            thread_num=num
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
        
           future_to_url = {executor.submit(self.__extract_house_info__task__,id): id for id in range(0,int(thread_num))}
           
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
        self.region_page_content_queue.join()
        self.log.info('总共提取{}个房屋url'.format(self.house_url_queue.qsize()))
        file_name=self.root_flie_dir+'/file/city/xian/region/'+self.house_url_list[0][2]
    
        self.__mkdir___(file_name)
        file_name=file_name+'/'+self.house_url_list[0][2]+'_url.csv'
    
        self.__save_region_house_url_(file_name)
        end=time.time()
        total_time=end-start
        self.log.info('extract house url :{}'.format(total_time))

    def __save_region_house_url_(self,file_name):
        
        self.__save_file__(file_name,self.house_url_list)
        self.house_url_list.clear()
        

    
    def __get_region_house_page_task__(self,id):
        '''
        request the house page of lianjia
        '''
      
        i=0
        n=0
        while True:
            n=n+1
            data=self.region_expand_url_queue.get()
            i=i+1
            self.region_expand_url_queue.task_done()
            
            if i<10*n:
                time.sleep(n)
            
            html=self.__request_page__(data[1])
            
            print(data[1])
            if len(html)!=0:
                data[1]=html
                new_data=[]
                new_data.append(data[1])
                new_data.append(html)
                self.region_page_content_list.append(new_data)
            
                self.region_page_content_queue.put(data)
            else:
                self.region_expand_url_queue.put(data)
                print('region_expand_url_queue put {0}'.format(data[1]))
            if self.region_expand_url_queue.empty():
                break;

        self.log.debug('get house page thread{}: executor {} task done'.format(id,i))
        return True

    def get_region_house_page(self):
        '''
        concurrently request every page  that you want to search from lianjia
        '''
        start=time.time()   
        
        
        thread_num=int(self.config.get('thread','get_region_house_page_thread_num'))

        num=self.region_expand_url_queue.qsize()
        if num<thread_num:
            thread_num=num
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
           
            future_to_url = {executor.submit(self.__get_region_house_page_task__,id): id for id in range(0,int(thread_num))}
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
        self.region_expand_url_queue.join()
        size=self.region_page_content_queue.qsize()
        self.log.info('总共{}个页面'.format(size))
        if size==0:
            return False
        file_name=self.root_flie_dir+'/file/city/xian/region/'+self.region_expand_url_list[0][0]+'/page'
        self.region_expand_url_list.clear()
        self.__mkdir___(file_name)
    
        self.__save_region_house_page_(file_name)
        end=time.time()
        total_time=end-start
        self.log.info('get house page :{}'.format(total_time))
        return True

    def __save_region_house_page_(self,file_name):
        i=0
        for data in self.region_page_content_list:
            
            name=file_name+'/pg{0}'.format(i)+'.html'
            i=i+1
            self.__save_file_page__(name,data[1])
        self.region_page_content_list.clear()

    def __save_file_page__(self,file_name,data):
        with open(file_name,'w') as f:
    
            f.write(data)
    
      
    def __extract_region_url_total_num__(self,data,page):
        '''
        extract all href of house page from tag of bigImgList 
        '''
        
        if data[0]!='lintong':
            return
        
        soup=BeautifulSoup(page,'lxml')

        for div in soup.find(class_="total").children:
            if div.name=='span':
                
                page_total_num=int(div.string)/self.num_page_per
                page_total_num_int=int(div.string)//self.num_page_per

                if page_total_num>page_total_num_int:
                    page_total_num=page_total_num_int+1
                
                for i in range(1,page_total_num+1):
                    url=data[1]+'pg{0}'.format(i)
                    print(url)
                    new_data=[]
                    new_data.append(data[0])
                    new_data.append(url)
                    self.region_expand_url_queue.put(new_data)
                    self.region_expand_url_list.append(new_data)
                    
           

                                
    
    def __expand_region_url_task__(self,id):
        '''
        request the house page of lianjia
        '''
        i=0
        while True:
            data=self.region_url_queue.get()
            i=i+1
            self.region_url_queue.task_done()
            html=self.__request_page__(data[1])
            #print(data[1])
            if len(html)!=0:
                
                self.__extract_region_url_total_num__(data,html)
            else:
                return False
            if self.region_url_queue.empty():
                break;

        self.log.debug('__expand_region_url_task__ thread{}: executor {} task done'.format(id,i))
        return True

    def expand_region_url(self):
        '''
        concurrently request every page  that you want to search from lianjia
        '''
        start=time.time()   
        
        
        thread_num=self.config.get('thread','expand_region_url_thread_num')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(thread_num)) as executor:
           
            future_to_url = {executor.submit(self.__expand_region_url_task__,id): id for id in range(0,int(thread_num))}
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
        self.region_url_queue.join()
        size=self.region_expand_url_queue.qsize()
        self.log.info('总共{}个页面'.format(size))
        if size==0:
            return False
        file_name=self.root_flie_dir+'/file/city/xian/region/'+self.region_expand_url_list[0][0]
        
        self.__mkdir___(file_name)
        file_name=file_name+'/'+self.region_expand_url_list[0][0]+'.csv'

    
        self.__save_expand_region_url_info__(file_name)
        end=time.time()
        total_time=end-start
        self.log.info(
            'get house page :{}'.format(total_time))
        return True

    def __save_expand_region_url_info__(self,file_name):
        self.__save_file__(file_name,self.region_expand_url_list)
        
    
    def __mkdir___(self,path):
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)

    def __save_region_info__(self,file_name):
        datas=[]
        for i in range(1,self.region_url_queue.qsize()):
            regions=self.region_url_queue.get()
            self.region_url_queue.task_done()
            data=[]
            for region in regions:
                data.append(region)
            datas.append(data)
        self.__save_file__(file_name,datas)


    def __save_file__(self,file_name,data):
        with open(file_name,'w') as f:
            out_csv=csv.writer(f)
            
            if type(data)==list:
                for dt in data:
                    out_csv.writerow(dt)
            else:
                out_csv.writerow(data)
    
     
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
   
    def __extract_region_url__(self,page):
        soup=BeautifulSoup(page,'lxml')
        for div in soup.find(attrs={"data-role": "ershoufang"}).children:
            if type(div)!=str:
                for href in div:
                    if type(href)!=str:
                        if href.name=='a':
                            print(href['href'])
                            regions=href['href'].split('/')
                            region=[]
                            if len(regions)>1:
                                print(regions[len(regions)-2])
                                region.append(regions[len(regions)-2])
                            url=self.prefix_url+href['href']
                            region.append(url)
                            self.region_url_queue.put(region)
        

    def get_root_page_house_info(self):
        '''
        concurrently request every page  that you want to search from lianjia
        '''
        start=time.time()   
        
        
        page=self.__request_page__(self.root_url)
        self.__extract_region_url__(page)
        #self.__save_region_info__(self.exe_path+'/file/city/xian/xian.csv')
        
        end=time.time()
        total_time=end-start
        self.log.info('get house page :{}'.format(total_time))
        print(self.region_url_queue.qsize())
        return True


class ConsumerDetailPageThread(threading.Thread):

    def __init__(self,name,house_url_detail_page_queue,root_url,debug,config,log):
        
        threading.Thread.__init__(self)
        self.config=config
        self.name=name
        self.exe_path=self.config.get('file','exe_path')
        self.house_url_detail_page_queue=house_url_detail_page_queue
        self.root_flie_dir=self.config.get('dir','root_file_dir')
        self.save_detail_page_num=0
        self.stop=False
        self.retry=int(config.get('request','retry_time'))
        self.retry_time_interval=int(config.get('request','retry_time_interval'))
        self.request_time_interval=int(config.get('request','request_time_interval'))
        self.setDaemon(True)
        self.log=log

    def __save_file_page__(self,file_name,data):
        with open(file_name,'w') as f:
    
            f.write(data)

    def __mkdir___(self,path):
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)

    def __save_page__(self,id):
    
        '''
        log on the site firstly. then save the cookie that site send .
        '''
        i=0
        n=1
        while True:
            
            data=self.house_url_detail_page_queue.get()
            i=i+1
            self.house_url_detail_page_queue.task_done()
            file_name=self.root_flie_dir+'/file/city/xian/region/'+data.region+'/url_detail_page'
    
            self.__mkdir___(file_name)
            name=file_name+'/'+data.house_id+'.html'
        
            self.__save_file_page__(name,data.house_detail_page)
            self.save_detail_page_num=self.save_detail_page_num+1
            print('save detail page: {}'.format(name))
                
            #print(html)
        
        self.log.debug('__save_page__ thread{}:executor {} task'.format(id,i))
        return True

    def save_detail_page(self):
        start=time.time()
        thread_num=int(self.config.get('thread','get_house_detail_page_thread_num'))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
           
            future_to_url = {executor.submit(self.__save_page__,id): id for id in range(0,int(thread_num))}
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

        self.house_url_detail_page_queue.join()
        self.log.info('总共保存{}个房屋详情页'.format(self.save_detail_page_num))
       
        end=time.time()
        total_time=end-start
        self.log.info('save_detail_page :{}'.format(total_time))
        return True

    def run(self):

        self.save_detail_page()

class HouseInfo:

    def __init__(self):
        self.house_detail=HouseDetail()
        self.publish_time=''
        self.focus_num=''
        self.href=''
        self.house_id=''
        self.house_detail_page=''
        self.neighborhood_id=''
        self.region=''
        
    def to_string(self):
        return [self.publish_time,self.focus_num,self.href,self.house_id]+self.house_detail.to_string()

class HouseDetail:

    def __init__(self):
        self.total_price=''
        self.average_price=''
        self.area=''
        self.layout=''
        self.dress=''
        self.tongtou=''
    def to_string(self):
        return [self.total_price,self.average_price,self.area,self.layout,self.dress,self.tongtou]
   


