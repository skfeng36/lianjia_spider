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
from thread import handle_house_thread
from thread import handle_concurrent_house_thread
import  signal
from util import signal_handle

if __name__ == '__main__':

    exe_path=sys.path[0]
    house_name='泾渭上城'
    concurrent=True
    config=configparser.ConfigParser()
    config.read(exe_path+'/conf/config.ini')

    sinal_handle=signal_handle.SignalHandle(signal.SIG_IGN)

    
    concurrent_house_thread=handle_concurrent_house_thread.ConcurrentGetHouseThread('concurrent_get_house',exe_path,house_name,0,config=config)
    concurrent_house_thread.start()
    house_server_thread=handle_house_thread.HouseServerThread('server',exe_path+'/file/house.html')
    house_server_thread.start()
    house_server_thread.join()
    concurrent_house_thread.join()







 


    
