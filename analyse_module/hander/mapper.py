'''
analyse house info module
'''
import os 
import csv
import sys
from util import csv2html

class Mapper:
    '''
    analyse house informations from the website.
    '''

    def __init__(self,house_detail_dict,config):
        self.house_detail_dict=house_detail_dict
    
        self.config=config
        
        self.exe_path=self.config.get('file','exe_path')
        self.root_file_dir=self.config.get('dir','root_file_dir')
        self.report_form_dir=self.config.get('dir','report_file_dir')
        self.mapping_dict={}

    def __mkdir___(self,path):
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)

    def output_mapping_file(self):
        '''
        output
        '''
        self.mapping_file=self.root_file_dir+self.report_form_dir+'mapping.csv'
       
        for neighborhood in self.house_detail_dict:
            house_output_file_dir=self.root_file_dir+self.report_form_dir+self.house_detail_dict[neighborhood][0].region;
            house_output_file_name=house_output_file_dir+'/'+neighborhood+'.html'
            self.mapping_dict[neighborhood]=house_output_file_name
        
        old_mapping_file_dict={}
        with open(self.mapping_file) as f:
                in_csv=csv.reader(f)
                for row in in_csv:
                    old_mapping_file_dict[row[0]]=row[1]
        if neighborhood not in old_mapping_file_dict:        
            with open(self.mapping_file,'a') as f:
                out_csv=csv.writer(f)
                for neighborhood in self.mapping_dict:
                    out_csv.writerow([neighborhood,self.mapping_dict[neighborhood]])
    



