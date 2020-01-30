'''

'''

from http.server import HTTPServer, BaseHTTPRequestHandler  # Py 3


def make_request_house_info_handler(html_content):
    class RequestHouseInfoHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):

            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        def do_GET(self):

            self.send_response(200)

            if self.path == '/house':
                self.send_header('Content-Type', 'text/html;charset=utf-8')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))

            else:

                html = ' '
                self.wfile.write(html.encode('utf-8'))

    return RequestHouseInfoHandler
