#!/home/sk/anaconda3/bin/python

from net import request_house_info
from hander import extract_page_data
from concurrent_hander import concurrent_request
import sys
import time
from  hander import analyse
import configparser
from util import csv2html
from net import http_server_monitor
from http.server import HTTPServer,BaseHTTPRequestHandler
from thread import handle_house_spider_monitor
from thread import handle_house_spider_thread
import  signal
from util import signal_handle
from util import logging_handle
import logging

if __name__ == '__main__':

    exe_path=sys.path[0]

    root_url='https://xa.lianjia.com/ershoufang/'

    concurrent=True
    config=configparser.ConfigParser()
    config.read(exe_path+'/conf/config.ini')
    config.set('file','exe_path',exe_path)


    signal_handler=signal_handle.SignalHandle(signal.SIG_IGN)
    log=logging_handle.Log(exe_path,logging.DEBUG).loger()

    
    concurrent_house_thread=handle_house_spider_thread.ConcurrentGetHouseThread('concurrent_get_house',root_url,0,config=config,log=log)
    concurrent_house_thread.start()
    #house_server_thread=handle_house_spider_monitor.HouseServerThread('server_monitor',exe_path+'/file/house.html',exe_path+'/page/index.html',log,config)
    #house_server_thread.start()
    #house_server_thread.join()
    concurrent_house_thread.join()







 


    
