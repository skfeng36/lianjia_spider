#!/home/sk/anaconda3/bin/python

import sys
import time
import configparser
from util import csv2html
from http.server import HTTPServer,BaseHTTPRequestHandler
from thread import handle_house_service_thread
import  signal
from util import signal_handle
from util import logging_handle
import logging

if __name__ == '__main__':

    exe_path=sys.path[0]
    
    config=configparser.ConfigParser()
    config.read(exe_path+'/conf/config.ini')
    config.set('file','exe_path',exe_path)

    signal_handler=signal_handle.SignalHandle(signal.SIG_IGN)
    log=logging_handle.Log(exe_path,logging.INFO).loger()

    house_server_thread=handle_house_service_thread.HouseServerThread('server',exe_path+'/file/house.html',exe_path+'/page/index.html',log,config)
    house_server_thread.start()
    house_server_thread.join()








 


    
