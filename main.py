#!/home/sk/anaconda3/bin/python

from net import request_house_info
from hander import extract_page_data
from concurrent_hander import concurrent_request
import sys
import time
from  hander import analyse

if __name__ == '__main__':

    exe_path=sys.path[0]
    house_name='泾渭上城'
    concurrent=True

    if not concurrent:

        house_info=request_house_info.HouseInfo(exe_path,house_name=house_name,debug=0)
        ret=False
        ret=house_info.get_house_page_info()
        if not ret :
            exit(1)
        extract_house=extract_page_data.ExtractHouseInfo(house_info.house_page_content_list,house_info.house_detail_info_url)
        extract_house.extract_house_info()
        extract_house.extract_house_detail(house_info.house_detail_page_list)
    else:

        current_hander=concurrent_request.ConcurrentHander(exe_path,house_name,0)
        start=time.time()
        ret=current_hander.concurrent_get_house_page_info()
        if not ret:
            print('get house page failure!')
            exit(1)
        current_hander.concurrent_extract_house_info()
        current_hander.concurrent_get_house_detail_page()
        current_hander.concurrent_extract_house_detail()
        end=time.time()
        total_time=end-start
        print(total_time)
        analyse_house=analyse.AnalyseHouse(current_hander.house_detail_info_queue)
        analyse_house.output_house_info(exe_path+'/file/house.csv')

 


    
