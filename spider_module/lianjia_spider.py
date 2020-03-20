#!/home/sk/anaconda3/bin/python

import sys
import os
import configparser
from net import http_server_monitor
from http.server import HTTPServer,BaseHTTPRequestHandler

from thread import handle_house_spider_thread
import  signal
sys.path.append("..")

from util import signal_handle
from util import logging_handle
import logging

if __name__ == '__main__':

    fast_search_name=''
    if len(sys.argv)>1:
        fast_search_name=sys.argv[1]
    

    root_url='https://xa.lianjia.com/ershoufang/'

    exe_path=sys.path[0]
    pwd = os.getcwd()
    father_path=os.path.abspath(os.path.dirname(pwd)+os.path.sep+".")

    config=configparser.ConfigParser()
    config.read(father_path+'/conf/config.ini')
    config.set('file','exe_path',exe_path)

    signal_handler=signal_handle.SignalHandle(signal.SIG_IGN)
    log=logging_handle.Log(father_path,logging.DEBUG).loger()

    
    concurrent_house_thread=handle_house_spider_thread.ConcurrentGetHouseThread('get_house',root_url,fast_search_name,0,config=config,log=log)
    concurrent_house_thread.start()
    #house_server_thread=handle_house_spider_monitor.HouseServerThread('server_monitor',exe_path+'/file/house.html',exe_path+'/page/index.html',log,config)
    #house_server_thread.start()
    #house_server_thread.join()
    concurrent_house_thread.join()







 


    
