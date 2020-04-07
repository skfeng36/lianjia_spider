'''
analyse house info module
'''

import csv
import sys
import queue
import os
import concurrent.futures
import time
from bs4 import BeautifulSoup
from super_thread import thread_pool

class Analyse(thread_pool.Task):
    '''
    analyse house informations from the website.
    '''
    
    def __init__(self,config,log):
        thread_pool.Task.__init__(self,'analyse_task')
        self.log=log
        self.house_file_name=[]
        self.house_detail_info_queue=queue.Queue()
        self.config=config
        self.exe_path=self.config.get('file','exe_path')
        self.root_file_dir=self.config.get('dir','root_file_dir')
        self.houe_file_root=self.root_file_dir+self.config.get('dir','house_file_dir')
        self.house_files={} #{regin:[house1,house2]}
        self.house_files_queue=queue.Queue()
        self.house_file_page_queue=queue.Queue()

        self.house_info_queue=queue.Queue()

        self.house_detail_info_list=[]

        self.house_detail_dict={}

        self.file_level=0
        self.stop=False
    
    def run(self):
         while not self.stop :
            start=time.time()
            retry=self.retry
            self.clear()
            self.log.info('get_house_file start......')

            #self.analyse.get_house_file()
            self.load_house_file()
            self.log.info('get_house_file finished.....')
            self.log.info('construct_house_infos start......')

            self.construct_house_infos()
            self.log.info('construct_house_infos finished......')
            self.log.info('extract_house_detail start......')

            self.extract_house_detail()
            self.log.info('extract_house_detail finished......')
            self.log.info('reduce start......')

            self.reduce()
            self.log.info('reduce finished......')
            self.log.info('ReportForm start......')


            end=time.time()
            total_time=end-start
            self.log.info(total_time)
            time.sleep(self.request_time_interval)

    def clear(self):
        self.house_detail_info_queue=queue.Queue()
        self.house_files={} #{regin:[house1,house2]}
        self.house_files_queue=queue.Queue()
        self.house_file_page_queue=queue.Queue()

        self.house_info_queue=queue.Queue()

    def load_house_file(self):
        file_name=self.houe_file_root+'/update_url.csv'
        print(file_name)
        with open(file_name) as f:
            csv_file=csv.reader(f)
            for row in csv_file:
                if row[1] in self.house_files:
                    self.house_files[row[1]].append(row[0])
                else:
                    data=[]
                    data.append(row[0])
                    self.house_files[row[1]]=data


    def get_house_file(self,level=0,data='',path=''):
        if len(path)==0:
            path=self.houe_file_root
        dir_or_files = os.listdir(path)
        for dir_file in dir_or_files:
            dir_file_path = os.path.join(path,dir_file)
            if os.path.isdir(dir_file_path):
                if level==0:
                    data=dir_file
                if dir_file=='url_detail_page':
                    self.house_files[data]=[]
                   
                file_level=level+1
                self.get_house_file(file_level,data,dir_file_path)
                
            else:
                if dir_file_path.find('.html')!=-1:
                    if len(data)>0:
                        if data in self.house_files:
                            file_list=self.house_files[data]
                            file_list.append(dir_file_path)
                            print(dir_file_path)
    
    def __get_house_page__(self,id):
        '''
        extract all href of house page and save it to house_detail_info_url
        '''
        
        i=0
        while True:
            data=self.house_files_queue.get(block=False)
            i=i+1
            self.house_files_queue.task_done()
            
            try:
                page=self.__read_file__(data.house_file)
                data.house_page=page
                self.house_file_page_queue.put(data)
            except:
                print('__get_house_page__ unknown except')
                return False
            if self.house_files_queue.empty():
                break;

        self.log.debug('get house page thread{}: executor {} task done'.format(id,i))
        return True

    def __read_file__(self,file_name):
        with open(file_name, 'r') as f:
            page=f.read()
        return page
            
    
    def construct_house_infos(self):    
        start=time.time()

        for (key, value) in self.house_files.items():
            for val in value:
                house_data=HouseData()
                house_data.region=key
                house_data.house_file=val
                print(house_data.to_string())
                self.house_files_queue.put(house_data)
    
        thread_num=int(self.config.get('thread','get_house_detail_page_thread_num'))
        num=self.house_files_queue.qsize()
        if num==0:
            return
        if num<thread_num:
            thread_num=num
        print(thread_num)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(thread_num)) as executor:
        
           future_to_url = {executor.submit(self.__get_house_page__,id): id for id in range(0,int(thread_num))}
           
           for future in concurrent.futures.as_completed(future_to_url):
                id = future_to_url[future]
                try:
                    ret = future.result()
                except Exception as exc:
                    print('%r construct_house_infos generated an exception: %s' % (id, exc))
                    return False
                else:
                    if not ret:
                        return ret       
        self.house_files_queue.join()
        self.log.info('总共提取{}个房屋'.format(self.house_file_page_queue.qsize()))
        end=time.time()
        total_time=end-start
        self.log.info('extract house url :{}'.format(total_time))

    def __extract_house_detail__(self,id):
        '''
        extract all house information from every detail url and save it to house_detail_info_list
        '''
        i=0
        house_detail_dict={}

        while True :
            data=self.house_file_page_queue.get()
            page=data.house_page
            i=i+1
            self.house_file_page_queue.task_done()
            names=data.house_file.split('/')
            if len(names)>0:
                houseids=names[len(names)-1].split('.')

            house_info=HouseInfo()
            house_info.region=data.region
            if len(houseids)>1:
                house_info.house_id=houseids[0]
            house_detail=house_info.house_detail
            
            soup=BeautifulSoup(page,'lxml')
            for di in soup.find(class_="transaction").children:
                if di.name=='div':
                    if di['class'][0]=='content':
                        for ul in di.children:
                            if ul.name=='ul':
                                for span in ul.children:
                                    if span.name=='li':
                                        for d in span.children:
                                            if d.name=='span':
                                                if d.string!='挂牌时间':
                                                    house_info.publish_time=d.string
                                        break       
                                                
            for di in soup.find(class_="sellDetailHeader").children:
                if di.name=='div':
                    for ul in di.children:
                        if ul.name=='div':
                            for ul2 in ul.children:
                                if ul2.name=='div':
                                    for ul3 in ul2.children:
                                        if ul3.name=='div':
                                            for ul4 in ul3.children:
                                                if ul4.name=='div':
                                                    if ul4['class'][0]=='action':
                                                        for ul5 in ul4.children:
                                                            if ul5.name=='span':
                                                                if ul5['class'][0]=='count':
                                                                    house_info.focus_num=ul5.string
                                                    
                                                    break
                                                
                                           
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
                        if item['class'][0]=='aroundInfo':
                            for div in item.children:
                                if div['class'][0]=='communityName':
                                
                                    for di in div.children:
                                        if di.name=='a':
                                            if di['class'][0]=='info':
                                                house_info.neighborhodd_name=di.string
                                                                                      
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
            self.house_info_queue.put(house_info)
            if house_info.neighborhodd_name in house_detail_dict:
                house_detail_dict[house_info.neighborhodd_name].append(house_info)
            else:
                house_info_list=[]
                house_info_list.append(house_info)
                house_detail_dict[house_info.neighborhodd_name]=house_info_list
                print(house_info.to_string())

            
            #print(house_info.to_string())

            if self.house_file_page_queue.empty():
                break;

        self.log.debug('extract house detail thread{}:executor {} task'.format(id,i))
        return house_detail_dict
        
    def extract_house_detail(self):
        start=time.time()
        thread_num=int(self.config.get('thread','extract_house_detail_thread_num'))
        num=self.house_file_page_queue.qsize()
        if num==0:
            return
        if num<thread_num:
            thread_num=num
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(thread_num)) as executor:
           
            future_to_url = {executor.submit(self.__extract_house_detail__,id): id for id in range(0,int(thread_num))}
            for future in concurrent.futures.as_completed(future_to_url):
                id = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    self.log.debug('%r extract_house_detail generated an exception: %s' % (id, exc))
                else:
                    self.log.debug('extract house detail thread:{} is done'.format(id))
                    self.house_detail_info_list.append(data)
        self.house_file_page_queue.join()
        self.log.info('总共提取{}个房屋详细信息'.format(self.house_info_queue.qsize()))
        end=time.time()
        total_time=end-start
        self.log.info('extract house detail :{}'.format(total_time))

    def reduce(self):
        
        house_detail_dict={}
        for data in self.house_detail_info_list:
        
            for key in data:
            
                if key in house_detail_dict:
                    
                    house_detail_dict[key]=house_detail_dict[key]+data[key]

                else:
                    house_info_list=data[key]
                    house_detail_dict[key]=house_info_list
                    
        self.house_detail_dict=house_detail_dict
        
    
    
class HouseData:

    def __init__(self):
        self.region=''
        self.house_file=''
        self.house_page=''
    def to_string(self):
        return [self.region,self.house_file]
    
class HouseInfo:
    
    def __init__(self):
        self.house_detail=HouseDetail()
        self.publish_time=''
        self.focus_num=''
        self.href=''
        self.house_id=''
        self.house_detail_page=''
        self.neighborhood_id=''
        self.neighborhodd_name=''
        self.region=''
        
    def to_string(self):
        return [self.neighborhodd_name,self.publish_time,self.focus_num,self.href,self.house_id]+self.house_detail.to_string()

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
   



