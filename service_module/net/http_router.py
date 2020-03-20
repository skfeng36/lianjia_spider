'''
this module is responsible for routering request 
'''

import csv
import sys
import configparser
import os

class Router:
    '''
    this class is a router that is responsible for mapping request.
    '''

    def __init__(self,config):
        self.config=config
        
        self.maping_dic={}
        self.version=0
        self.__load_mapping_data__()
    
        
        
    def __load_mapping_data__(self):
        root_dir=self.config.get('dir','root_file_dir')
        mapping_file_dir=self.config.get('dir','report_file_dir')
        mapping_file_name=self.config.get('file','mapping_file_name')
        
        with open(root_dir+mapping_file_dir+mapping_file_name) as input:
            info = os.fstat(input.fileno())
            if self.version!=info.st_mtime:
                csv_file=csv.reader(input)
                for row in csv_file:
                    self.maping_dic[row[0]]=row[1]
                self.version=info.st_atime

    def update(self):
        self.__load_mapping_data__()

    def mapping(self,path):
    
        if path in self.maping_dic:
            return self.maping_dic[path]
        else:
            return '/'
        
        


