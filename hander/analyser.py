'''
analyse house info module
'''

import csv
import sys
import queue
import os

class Analyse:
    '''
    analyse house informations from the website.
    '''
    
    def __init__(self,config,log):
        self.log=log
        self.house_file_name=[]
        self.house_detail_info_queue=queue.Queue()
        self.config=config
        self.exe_path=self.config.get('file','exe_path')

        self.houe_file_root=self.exe_path+self.config.get('file','house_file_root')
        self.house_files={} #{regin:[house1,house2]}
        self.house_files_queue=queue.Queue()

        self.file_level=0
        
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
                    house_data=HouseData()
                    house_data.region=data
                    house_data.house_list.append(self.house_files[data])
                    self.house_files_queue.put(house_data)
                file_level=level+1
                self.get_house_file(file_level,data,dir_file_path)
                
            else:
                if dir_file_path.find('.html')!=-1:
                    if len(data)>0:
                        if data in self.house_files:
                            file_list=self.house_files[data]
                            file_list.append(dir_file_path)
    
    def construct_house_infos(self):
        pass

class HouseData:

    def __init__(self):
        self.region=''
        self.house_list=[]

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
   



