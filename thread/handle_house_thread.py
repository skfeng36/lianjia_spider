'''
handle_house_thread module handles http request.
'''

import threading
from net import http_server
from http.server import HTTPServer,BaseHTTPRequestHandler
from util import csv2html
import os

'''
HtmlData stores the html data from house.html file
'''

class HtmlData:
    version=0
    content=''

class HouseServerThread(threading.Thread):

    def __init__(self,name,html_file_name,log):
        threading.Thread.__init__(self)
        self.name=name
        self.html_file_name=html_file_name
        self.html_data=HtmlData()
        self.RequestHouseInfoHandler=http_server.make_request_house_info_handler(self.html_data)
        self.stop=False
        self.version=0
        self.setDaemon(True)
        self.log=log

    def __update_data__(self):
        '''
        udpate http_data when house.html file was updated .
        '''
        with open(self.html_file_name) as input_file:
            info = os.fstat(input_file.fileno())
            if self.version!=info.st_mtime:
                self.html_data.content=input_file.read()
                self.version=info.st_atime
                self.html_data.version=self.version
        
    def set_stop(self,stop):
        self.stop=stop

    def run(self):
        '''
        run function filstly handle http request.
        secondly it updates html data from updated house.html file
        '''

        server_address =('127.0.0.1',8888)
        self.log.info('thread:{0} http server listening.....'.format(self.name))
        with HTTPServer(server_address,self.RequestHouseInfoHandler) as httpd:
            while not self.stop:
                self.__update_data__()
                httpd.handle_request()
            

            
