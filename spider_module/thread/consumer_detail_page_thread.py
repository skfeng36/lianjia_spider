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
        self.lock=threading.Lock()

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
            self.lock.acquire()
            self.save_detail_page_num=self.save_detail_page_num+1
            self.lock.release()
            print('save detail page num:{0}'.format(self.save_detail_page_num))
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
                    self.log.debug('%r save_detail_page generated an exception: %s' % (id, exc))
                    
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
