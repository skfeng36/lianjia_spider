#!/home/sk/anaconda3/bin/python

from net import request_house_info
from hander import extract_page_data
from concurrent_hander import concurrent_request
import sys
import time
from  hander import analyse
import configparser
from util import csv2html
from net import http_server
from http.server import HTTPServer,BaseHTTPRequestHandler

if __name__ == '__main__':

    exe_path=sys.path[0]
    house_name='泾渭上城'
    concurrent=True
    config=configparser.ConfigParser()
    config.read(exe_path+'/conf/config.ini')

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

        current_hander=concurrent_request.ConcurrentHander(exe_path,house_name,0,config=config)
        start=time.time()
        print('concurrent_get_house_page_info start......')
        ret=current_hander.concurrent_get_house_page_info()
        print('concurrent_get_houst_page_info finished.....')
        if not ret:
            print('get house page failure!')
            exit(1)
        print('concurrent_extract_house_info start....')
        current_hander.concurrent_extract_house_info()
        print('concurrent_extract_house_info finished....')

        print('concurrent_get_house_detail_page start....')
        ret=current_hander.concurrent_get_house_detail_page()
        if not ret:
            print('get house detail page failure!')
            exit(1)
        print('concurrent_get_house_detail_page finished....')

        print('concurrent_extract_house_detail start....')
        current_hander.concurrent_extract_house_detail()
        print('concurrent_extract_house_detail finished')
        end=time.time()
        total_time=end-start
        print(total_time)
        analyse_house=analyse.AnalyseHouse(current_hander.house_detail_info_queue)
        analyse_house.output_house_info(exe_path+'/file/house.csv')
        csv2html=csv2html.CSV2HTML(exe_path+'/file/house.csv')
        csv2html.to_html_file()

        server_address =('127.0.0.1',8888)
        print('http server listening.....')
        with HTTPServer(server_address,http_server.make_request_house_info_handler(csv2html.to_html_string()),csv2html.to_html_string()) as httpd:
            httpd.serve_forever()






 


    
