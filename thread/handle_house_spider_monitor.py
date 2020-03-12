'''
handle_house_thread module handles http request.
'''

import threading
from net import http_server_monitor
from http.server import HTTPServer,BaseHTTPRequestHandler
from util import csv2html
import os
from net import http_router

'''
HtmlData stores the html data from house.html file
'''
import configparser

class HtmlData:
    def __init__(self,config,router,version=0,content='',index_content=''):
        
        self.config=config
        self.router=router
        self.version=version
        self.content=content
        self.index_content=index_content
        

class HouseServerThread(threading.Thread):

    def __init__(self,name,html_file_name,index_file_name,log,config):
        threading.Thread.__init__(self)
        self.name=name
        self.html_file_name=html_file_name
        self.index_file_name=index_file_name
        self.config=config
        self.router=http_router.Router(self.config)
        self.html_data=HtmlData(self.config,self.router)

        self.RequestHouseInfoHandler=http_server.make_request_house_info_handler(self.html_data)
        self.stop=False
        self.version=0
        self.setDaemon(True)
        self.log=log

    def __update_data__(self):
        '''
        udpate http_data when house.html file was updated .
        '''
        try:
            with open(self.html_file_name) as input_file:
                info = os.fstat(input_file.fileno())
                if self.version!=info.st_mtime:
                    self.html_data.content=input_file.read()
                    self.version=info.st_atime
                    self.html_data.version=self.version
        
        except Exception as exc:
            self.html_data.content='waiting for few  minutes ,please!'
        
        try:
            with open(self.index_file_name) as input_file:
                info = os.fstat(input_file.fileno())
                self.html_data.index_content=input_file.read()
                    
        
        except Exception as exc:
            self.html_data.content='loading index page , waiting for few  minutes ,please!'
        
    def set_stop(self,stop):
        self.stop=stop

    def run(self):
        '''
        run function filstly handle http request.
        secondly it updates html data from updated house.html file
        '''

        server_address =('127.0.0.1',9999)
        self.log.info('thread:{0} http server listening.....'.format(self.name))
        with HTTPServer(server_address,self.RequestHouseInfoHandler) as httpd:
            while not self.stop:
                self.__update_data__()
                httpd.handle_request()
            

            
