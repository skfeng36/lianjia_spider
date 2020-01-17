#!/home/sk/anaconda3/bin/python

from net import request_house_info
from hander import extract_page_data
import sys

if __name__ == '__main__':
    exe_path=sys.path[0]
    house_name='泾渭上城'
    house_info=request_house_info.HouseInfo(exe_path,house_name=house_name,debug=0)
    ret=False
    ret=house_info.get_house_page_info()
    if not ret :
        exit(1)
    extract_house=extract_page_data.ExtractHouseInfo(house_info.house_page_content_list,house_info.house_detail_info_url)
    extract_house.extract_house_info()
    house_info.get_house_detail_page()
    extract_house.extract_house_detail(house_info.house_detail_page_list)


    