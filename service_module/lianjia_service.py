#!/home/sk/anaconda3/bin/python

import sys
import time
import os
import configparser
from http.server import HTTPServer,BaseHTTPRequestHandler
from thread import handle_house_service_thread
import  signal
sys.path.append("..")

from util import signal_handle
from util import logging_handle
import logging

if __name__ == '__main__':

    exe_path=sys.path[0]
    pwd = os.getcwd()
    father_path=os.path.abspath(os.path.dirname(pwd)+os.path.sep+".")

    config=configparser.ConfigParser()
    config.read(father_path+'/conf/config.ini')
    config.set('file','exe_path',exe_path)

    signal_handler=signal_handle.SignalHandle(signal.SIG_IGN)
    log=logging_handle.Log(father_path,logging.DEBUG).loger()

    house_server_thread=handle_house_service_thread.HouseServerThread('server',father_path+'/file/house.html',father_path+'/page/index.html',log,config)
    house_server_thread.start()
    house_server_thread.join()








 


    
