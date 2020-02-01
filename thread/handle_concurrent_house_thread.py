'''

'''

import threading
from net import http_server
from http.server import HTTPServer,BaseHTTPRequestHandler
from util import csv2html
from concurrent_hander import concurrent_request
from hander import analyse
from util import csv2html

import time
class ConcurrentGetHouseThread(threading.Thread):
    def __init__(self,name,exe_path,house_name,debug,config,log):
        
        threading.Thread.__init__(self)
        self.name=name
        self.current_hander=concurrent_request.ConcurrentHander(exe_path,house_name,0,config=config,log=log)
        self.exe_path=exe_path
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
            while retry>0:
                self.log.info('concurrent_get_house_page_info start......')
                ret=self.current_hander.concurrent_get_house_page_info()
                if not ret:
                    self.log.info('get house page failure!')
                    retry=retry-1
                    self.log.debug('get house page retry:{0}'.format(self.retry-retry))
                else:
                    break
            if not ret:
                self.current_hander.clear()
                time.sleep(self.retry_time_interval)
                continue

            self.log.info('concurrent_get_houst_page_info finished.....')

            self.log.info('concurrent_extract_house_info start....')
            self.current_hander.concurrent_extract_house_info()
            self.log.info('concurrent_extract_house_info finished....')

            retry=self.retry
            while retry>0:

                self.log.info('concurrent_get_house_detail_page start....')
                ret=self.current_hander.concurrent_get_house_detail_page()
                if not ret:
                    self.log.info('get house detail page failure!')
                    retry=retry-1
                    self.log.debug('get house detail page retry:{0}'.format(self.retry-retry))
                else:
                    break
            if not ret:
                self.current_hander.clear()
                time.sleep(self.retry_time_interval)
                continue

            self.log.info('concurrent_get_house_detail_page finished....')

            self.log.info('concurrent_extract_house_detail start....')
            self.current_hander.concurrent_extract_house_detail()
            self.log.info('concurrent_extract_house_detail finished')
            end=time.time()
            total_time=end-start
            self.log.info(total_time)
            analyse_house=analyse.AnalyseHouse(self.current_hander.house_detail_info_queue)
            analyse_house.output_house_info(self.exe_path+'/file/house.csv')
            house_csv2html=csv2html.CSV2HTML(self.exe_path+'/file/house.csv')
            house_csv2html.to_html_file()
            time.sleep(self.request_time_interval)