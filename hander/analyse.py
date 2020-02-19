'''
analyse house info module
'''

import csv
import sys

class AnalyseHouse:
    '''
    analyse house informations from the website.
    '''

    def __init__(self,house_detail_info_queue):
        self.house_detail_info_queue=house_detail_info_queue
        self.house_detail_info_list=[]
        while not self.house_detail_info_queue.empty():
            house=self.house_detail_info_queue.get()
            self.house_detail_info_list.append(house)
        

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


    def output_house_info(self,file_name):
        '''
        output
        '''

        with open(file_name,'w') as f:
            out_csv=csv.writer(f)
            self.house_detail_info_list.sort(key=self.__sort_by_total_price__)
            out_csv.writerow(['序号','房屋编号','面积','总价','装修情况','均价','发布时间','关注人数'])
            i=0
            for house in self.house_detail_info_list:
                i=i+1
                out_csv.writerow([str(i),'N'+house.house_id,house.house_detail.area,house.house_detail.total_price+'万',house.house_detail.dress,house.house_detail.average_price+'元/平米',house.publish_time,house.focus_num])


