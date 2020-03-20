'''

'''

import threading
import sys
from net import http_server_monitor
from http.server import HTTPServer,BaseHTTPRequestHandler
sys.path.append("..")
from util import csv2html
from hander import analyser
from hander import report_form

import time
class AnalyseThread(threading.Thread):
    def __init__(self,name,debug,config,log):
        
        threading.Thread.__init__(self)
        self.config=config
        self.name=name
        self.exe_path=self.config.get('file','exe_path')

        self.analyse=analyser.Analyse(config=config,log=log)
        
    
        self.stop=False
        self.retry=int(config.get('request','retry_time'))
        self.retry_time_interval=int(config.get('request','retry_time_interval'))
        self.request_time_interval=int(config.get('request','request_time_interval'))
        self.setDaemon(True)
        self.log=log
        
    def run(self):
       
        while not self.stop :
            start=time.time()
            retry=self.retry
            self.analyse.clear()
            self.log.info('get_house_file start......')

            self.analyse.get_house_file()
            self.log.info('get_house_file finished.....')
            self.log.info('construct_house_infos start......')

            self.analyse.construct_house_infos()
            self.log.info('construct_house_infos finished......')
            self.log.info('extract_house_detail start......')

            self.analyse.extract_house_detail()
            self.log.info('extract_house_detail finished......')
            self.log.info('reduce start......')

            self.analyse.reduce()
            self.log.info('reduce finished......')
            self.log.info('ReportForm start......')

            form=report_form.ReportForm(self.analyse.house_detail_dict,self.config)
            self.log.info('ReportForm finished......')
            self.log.info('output_house_info start......')

            form.output_house_info()
            self.log.info('output_house_info finished......')
            self.log.info('construct_html_file start......')

            form.construct_html_file()
            self.log.info('construct_html_file finished......')
            self.log.info('build_mapping_file start......')
            
            form.build_mapping_file()
            self.log.info('build_mapping_file finished......')

            end=time.time()
            total_time=end-start
            self.log.info(total_time)
        
            time.sleep(self.request_time_interval)