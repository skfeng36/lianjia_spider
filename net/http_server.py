'''
make_request_house_info_handler is a function that return a RequestHouseInfoHandler class.

'''

from http.server import HTTPServer, BaseHTTPRequestHandler  # Py 3


def make_request_house_info_handler(html_data):
    '''
    RequestHouseInfoHandler is a subclass of BaseHTTPRequestHandler which handle people's requests for house information.
	
    '''

            
    class RequestHouseInfoHandler(BaseHTTPRequestHandler):

        def __init__(self, *args, **kwargs):

            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
        

        def do_GET(self):

            '''
            this function handles get request.
			'''
            self.send_response(200)
            request_line=self.path.split('?')
            if len(request_line)>0:
                path=request_line[0]
            else:
                path='/'
            print(path)
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
