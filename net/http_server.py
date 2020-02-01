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

            if self.path == '/house':
                self.send_header('Content-Type', 'text/html;charset=utf-8')
                self.end_headers()
                self.wfile.write(html_data.content.encode('utf-8'))

            else:

                html = ' '
                self.wfile.write(html.encode('utf-8'))

    return RequestHouseInfoHandler
