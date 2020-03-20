'''
make_request_house_info_handler is a function that return a RequestHouseInfoHandler class.

'''

from http.server import HTTPServer, BaseHTTPRequestHandler  # Py 3
import os 
import queue
import urllib.parse

def make_request_house_info_handler(html_data):
    '''
    RequestHouseInfoHandler is a subclass of BaseHTTPRequestHandler which handle people's requests for house information.
	
    '''
            
    class RequestHouseInfoHandler(BaseHTTPRequestHandler):

        
        def __init__(self, *args, **kwargs):

            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
        
        def __mapping_request__(self,request_path):
            return html_data.router.mapping(request_path)
            
        def __load_response__(self,request_path):
            request_path=urllib.parse.unquote(request_path)
            
            print(request_path)
            page_name=self.__mapping_request__(request_path)
            
            exe_path=html_data.config.get('file','exe_path')
            try:
                with open(page_name) as input_file:
                    html_data.content=input_file.read()
                    
            except Exception as exc:
                html_data.content='not found this page , waiting for few  minutes ,please!'
        
        

        def do_GET(self):

            '''
            this function handles get request.
			'''
            self.send_response(200)
            request_line=self.path.split('?')
            print(request_line)
            neighborhood_name=''
            if len(request_line)>0:
                path=request_line[0]
                if len(request_line)>1:
                    neighborhood_name=request_line[1]
                    parameter=neighborhood_name.split('=')
                    if len(parameter)>1:
                        neighborhood_name=parameter[1]
                
            else:
                path='/'
            print(neighborhood_name)
            
            self.__load_response__(neighborhood_name)
            if path == '/house':
                self.send_header('Content-Type', 'text/html;charset=utf-8')
                self.end_headers()
                self.wfile.write(html_data.content.encode('utf-8'))
            elif path=='/search':
                self.send_header('Content-Type', 'text/html;charset=utf-8')
                self.end_headers()
                self.wfile.write(html_data.content.encode('utf-8'))

            else:

                self.send_header('Content-Type', 'text/html;charset=utf-8')
                self.end_headers()
                self.wfile.write(html_data.index_content.encode('utf-8'))

    return RequestHouseInfoHandler
