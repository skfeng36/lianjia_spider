'''

'''

import threading
from net import http_server_monitor
from http.server import HTTPServer,BaseHTTPRequestHandler
from util import csv2html
from concurrent_hander import spider_house
from hander import analyser
from hander import report_form
from util import csv2html

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

            form=report_form.ReportForm(self.analyse.house_detail_dict,self.config)
            form.output_house_info()
            form.construct_html_file()
            

            '''
        
            end=time.time()
            total_time=end-start
            self.log.info(total_time)
            analyse_house=analyse.AnalyseHouse(self.current_hander.house_detail_info_queue,self.config)
            analyse_house.output_house_info()

            house_csv2html=csv2html.CSV2HTML(analyse_house.house_output_file_name)
            house_csv2html.to_html_file()
            '''
            time.sleep(self.request_time_interval)