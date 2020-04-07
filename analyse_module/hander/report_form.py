'''
analyse house info module
'''
import os 
import csv
import sys
from util import csv2html
from hander import mapper

class ReportForm:
    '''
    analyse house informations from the website.
    '''

    def __init__(self,house_detail_dict,config):
        self.house_detail_dict=house_detail_dict
    
        self.config=config
        
        self.exe_path=self.config.get('file','exe_path')
        self.root_file_dir=self.config.get('dir','root_file_dir')
        self.report_form_dir=self.config.get('dir','report_file_dir')
        self.house_file_name_list=[]
        self.mapper=mapper.Mapper(self.house_detail_dict,self.config)
        #self.house_output_file_name=exe_path+'/file/'+self.neighborhood_id+'.csv'
        

    def __sort_by_area__(self,elem):
        '''
        sort elem by it's area field.
        '''
        return float(elem.house_detail.area[0:len(elem.house_detail.area)-2])

    def __sort_by_total_price__(self,elem):
        '''
        sort elem by it's total price field
        '''
        return float(elem.house_detail.total_price)

    def __mkdir___(self,path):
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)

    def output_house_info(self):
        '''
        output
        '''
        
        for neighborhood in self.house_detail_dict:
            house_output_file_dir=self.root_file_dir+self.report_form_dir+self.house_detail_dict[neighborhood][0].region;
            house_output_file_name=house_output_file_dir+'/'+neighborhood+'.csv'
            self.house_file_name_list.append(house_output_file_name)
            self.__mkdir___(house_output_file_dir)
            
            with open(house_output_file_name,'w') as f:
                out_csv=csv.writer(f)
                self.house_detail_dict[neighborhood].sort(key=self.__sort_by_total_price__)
                
                out_csv.writerow(['序号','('+neighborhood+')房屋编号','面积','总价','装修情况','均价','发布时间','关注人数'])
                i=0
                for house in self.house_detail_dict[neighborhood]:
                    i=i+1
                    out_csv.writerow([str(i),'N'+house.house_id,house.house_detail.area,house.house_detail.total_price+'万',house.house_detail.dress,house.house_detail.average_price+'元/平米',house.publish_time,house.focus_num])
    
    def construct_html_file(self):
        for house_output_file_name in self.house_file_name_list:
            house_csv2html=csv2html.CSV2HTML(house_output_file_name)
            house_csv2html.to_html_file()
    
    def build_mapping_file(self):
        self.mapper.output_mapping_file()




