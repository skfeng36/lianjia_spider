"""
 CSV2HTML is a simple class to converts csv file into html file.
"""
import urllib.parse
import ssl
from urllib import request
import hashlib
import json
from http import cookiejar
import sys
from bs4 import BeautifulSoup
import concurrent.futures
import queue
import time
import csv

class CSV2HTML:
    '''
    CSV2HTML is a simple class to converts csv file into html file.

    '''

    def __init__(self,csv_file_name):
        self.csv_input_file=open(csv_file_name)
        self.csv_file=csv.reader(self.csv_input_file)
        self.html_file_name=csv_file_name.split('.')[0]+'.html'
        
        self.html_prefix='<html><head></head><body>'
        self.html_subfix='</body></html>'
        self.html_content=''
        self.html_content=self.html_content+self.html_prefix

    def __del__(self):
        self.csv_input_file.close()

    def to_html_file(self):
        '''
        converts csv file to html file
        '''
        with open(self.html_file_name,'w') as html_output:
            self.html_content=self.html_content+'<table border=\"1\">'
            for row in self.csv_file:
                self.html_content=self.html_content+'<tr>'
                for r in row:
                    self.html_content=self.html_content+'<td>{0}'.format(r)
                    self.html_content=self.html_content+'</td>'
                self.html_content=self.html_content+'</tr>'
            self.html_content=self.html_content+'</table>'
            self.html_content=self.html_content+self.html_subfix
            html_output.write(self.html_content)
                

    def to_html_string(self):
        '''
        return html string
        '''
        return self.html_content
    
