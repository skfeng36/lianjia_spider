#!/home/sk/anaconda3/bin/python

#from net import request_house_info
#from hander import extract_page_data
from thread import handle_house_analyse_thread
import sys
import os
import time
import configparser

import  signal
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

    
    analyse_house_thread=handle_house_analyse_thread.AnalyseThread('analyse',0,config=config,log=log)
    analyse_house_thread.start()
   
    analyse_house_thread.join()







 


    
