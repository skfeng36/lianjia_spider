"""
 cookie expires at some hours later when we log on site,
 so we need  take the  cookie that log on site  to request  site  every times 
"""
import hashlib
import json
import sys
from bs4 import BeautifulSoup

class ExtractHouseInfo :
    '''
    gets the lastest seconde-house information  of lianjia from the website(https://xa.lianjia.com/ershoufang/)
    '''
    def __init__(self,house_page_content_list,house_detail_info_url):

        self.house_page_content_list=house_page_content_list
        self.house_detail_info_url=house_detail_info_url
        self.house_detail_page_list=[]
        self.house_detail_info_list=[]
        
    '''

    '''
    def __extract_house_url__(self,soup):
        '''
        extract all href of house page from tag of bigImgList 
        '''
        for div in soup.find(class_="bigImgList").children:
            for img in div.children:
                if img['class'][0]=='img':
                    self.house_detail_info_url.append(img['href'])
                    
        
    def extract_house_info(self):
        '''
        extract all href of house page and save it to house_detail_info_url
        '''
        for page in self.house_page_content_list:
            soup=BeautifulSoup(page,'lxml')
            self.__extract_house_url__(soup)

        print(len(self.house_page_content_list))

        print(len(self.house_detail_info_url))
        print('extract_house_info done')

    def extract_house_detail(self,house_detail_page_list):
        '''
        extract all house information from every detail url and save it to house_detail_info_list
        '''
        print(len(house_detail_page_list))
        for page in house_detail_page_list:
            house_detail=HouseDetail()
            soup=BeautifulSoup(page,'lxml')
            for div in soup.find(class_="overview").children:
                if div['class'][0]=='content':
                    for item in div.children:
                        
                        if item['class'][0]=='price':
                            for span in item.children:
                                if span['class'][0]=='total':
                                    house_detail.total_price=span.string
                                if span['class'][0]=='text':
                                    for div in span.children:
                                        if div['class'][0]=='unitPrice':
                                            for span  in div.children:
                                                if span['class'][0]=='unitPriceValue':
                                                    for str in span.strings:
                                                        house_detail.average_price=str
                                                        break;
                        if item['class'][0]=='houseInfo':
                            for div in item.children:
                                if div['class'][0]=='area':
                                    for div2 in div.children:
                                        if div2['class'][0]=='mainInfo':
                                            house_detail.area=div2.string
                                if div['class'][0]=='room':
                                    for div2 in div.children:
                                        if div2['class'][0]=='mainInfo':
                                            house_detail.layout=div2.string
                                if div['class'][0]=='type':
                                    for div2 in div.children:
                                        if div2['class'][0]=='subInfo':
                                            house_detail.dress=div2.string                       
                                        if div2['class'][0]=='mainInfo':
                                            house_detail.tongtou=div2.string 
            self.house_detail_info_list.append(house_detail)
        print(len(self.house_detail_info_list))
        print('extract_house_detail done')

                                        

class HouseDetail:

    def __init__(self):
        self.house_id=''
        self.total_price=''
        self.average_price=''
        self.area=''
        self.layout=''
        self.dress=''
        self.tongtou=''



