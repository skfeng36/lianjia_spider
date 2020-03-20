'''

'''

import threading
from net import http_server_monitor
from http.server import HTTPServer,BaseHTTPRequestHandler

from hander import spider_house


import time
class ConcurrentGetHouseThread(threading.Thread):
    def __init__(self,name,root_url,debug,config,log):
        
        threading.Thread.__init__(self)
        self.config=config
        self.name=name
        self.exe_path=self.config.get('file','exe_path')

        self.current_hander=spider_house.ConcurrentHander(root_url,0,config=config,log=log)
    
        self.stop=False
        self.retry=int(config.get('request','retry_time'))
        self.retry_time_interval=int(config.get('request','retry_time_interval'))
        self.request_time_interval=int(config.get('request','request_time_interval'))
        self.setDaemon(True)
        self.log=log
        
    def run(self):

        
        self.current_hander.get_root_page_house_info()

        self.log.info('expand_region_url start......')

        self.current_hander.expand_region_url()
        self.log.info('expand_region_url finished.....')
       
        
        while not self.stop :
            start=time.time()
            retry=self.retry
            
            while retry>0:
                self.log.info('get_region_house_page start......')
                ret=self.current_hander.get_region_house_page()
                if not ret:
                    self.log.info('get_region_house_page failure!')
                    retry=retry-1
                    self.log.debug('get_region_house_page retry:{0}'.format(self.retry-retry))
                else:
                    break
            if not ret:
                self.current_hander.clear()
                time.sleep(self.retry_time_interval)
                continue

            self.log.info('get_region_house_page finished.....')
            
            self.log.info('extract_house_url_info start....')
            self.current_hander.extract_house_url_info()
            self.log.info('extract_house_url_info finished....')
            
            self.current_hander.save_detail_page()
            retry=self.retry
            while retry>0:

                self.log.info('get_house_url_detail_page start....')
                ret=self.current_hander.get_house_url_detail_page()
                if not ret:
                    self.log.info('get_house_url_detail_page failure!')
                    retry=retry-1
                    self.log.debug('get_house_url_detail_page retry:{0}'.format(self.retry-retry))
                else:
                    break
            if not ret:
                time.sleep(self.retry_time_interval)
                continue

            self.log.info('get_house_url_detail_page finished....')
        


            
            time.sleep(self.request_time_interval)