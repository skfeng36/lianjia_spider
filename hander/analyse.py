import csv
import sys

class AnalyseHouse:

    def __init__(self,house_detail_info_list):
        self.house_detail_info_liust=house_detail_info_list
        

    def save_file(self,file_name): 

        with open(file_name,'w') as f:
            out_csv=csv.writer(f)
