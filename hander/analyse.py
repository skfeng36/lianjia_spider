import csv
import sys

class AnalyseHouse:

    def __init__(self,house_detail_info_queue):
        self.house_detail_info_queue=house_detail_info_queue
        self.house_detail_info_list=[]
        while not self.house_detail_info_queue.empty():
            house=self.house_detail_info_queue.get()
            self.house_detail_info_list.append(house)
        

    def __sort_by_area__(self,elem):
        return float(elem.area[0:len(elem.area)-2])

    def save_file(self,file_name): 

        with open(file_name,'w') as f:
            out_csv=csv.writer(f)
            self.house_detail_info_list.sort(key=self.__sort_by_area__)
            out_csv.writerow(['房屋编号','面积','总价','装修情况','均价'])
            for house in self.house_detail_info_list:
                #print(house.to_string())
                out_csv.writerow(['N'+house.house_id,house.area,house.total_price+'万',house.dress,house.average_price+'元/平米'])


