from bs4 import BeautifulSoup
import requests
import re
import json
import time
import os

from pyquery import PyQuery as pq
from collections import OrderedDict
import pandas as pd

from urllib.request import urlretrieve


big_cate=[
# '其他類型buffet自助餐',
# '中式',
# '日式',
# '西式',
# '複合式',
# '碗粿',
# '其他小吃',  #其他小吃  48頁之後就沒爬了

# 府東街蔥油餅芋頭餅
# bigdata/eat/其他小吃/新營太子路沙鍋魚頭
# bigdata/eat/其他小吃/新營太子路沙鍋魚頭
# bigdata/eat/其他小吃/紜楓刈包
# bigdata/eat/其他小吃/巷仔內麵店


'鹹酥雞、炸雞排',
'筒仔米糕',
'藥燉排骨',
'焢肉飯',
'豬血糕',
'鵝肉',
'肉粽',
'四神湯',
'滷肉飯',
'滷味',
'鹹水雞',
'胡椒餅',
'米粉湯',
'蚵仔煎',
'臭豆腐',
'水煎包、生煎包',
'麵攤、麵店',
'肉圓',
'蔥油餅、蔥抓餅',
'刈包',
'麵線',
'棺材板']

photo_peak_folder="bigdata/eat/"
json_folder="bigdata/json_file/"

source_url="http://www.ipeen.com.tw/"

def want_to_get_shoplink(cate_all_page,kind):
	shop_link=[]

	for each_cate in cate_all_page:
		cate_html=requests.get(each_cate)
		cate_bf=BeautifulSoup(cate_html.text,"html.parser")
		stores = cate_bf.find_all('a',class_="a37 ga_tracking")
		for s in stores:
			if(s['href'][0:5]=="/shop"):
				shop_link.append("http://www.ipeen.com.tw"+s['href'])

	return shop_link,kind


# input the category all shop unique link list
# output the category all shop contents dict
def crowl_store_content(cate_all_page):


	q = pq(cate_all_page)
	columns_name = q('th').text()
	columns_name = [item for item in columns_name.split(" ") if item.split()]

	columns_name_content = q('td').text()



	neg_text_list = [item for item in columns_name_content.split(" ") if item.split()]

	dict_store_content = {}
	start = (neg_text_list.index(">")-2)

	for i in range(len(columns_name)):

		columns = columns_name.pop(0)

		if columns=='商家名稱':
			dict_store_content['商家名稱']=neg_text_list[start]
		elif columns=='商家分類':
			if neg_text_list[start+6]=='粵菜':
				dict_store_content['商家分類']=neg_text_list[start+7]
				dict_store_content['分類']=neg_text_list[start+4]
				start = start +7
			else:
				dict_store_content['商家分類']=neg_text_list[start+6]
				dict_store_content['分類']=neg_text_list[start+4]
				start = start +6
		elif columns=='電話':
			dict_store_content['電話']=neg_text_list[start]
		elif columns=='地址':
			dict_store_content['地址']=neg_text_list[start]
			start = start+1

		elif columns=='公休日':
			dict_store_content['公休日']=neg_text_list[start]
		elif columns=='營業時間':
			if neg_text_list[start]=='今日':
				start=start+1
				dict_store_content['營業時間']=neg_text_list[start]
			else:
				dict_store_content['營業時間']=neg_text_list[start]

		start = start + 1
		dict_store_content['網址']=cate_all_page


	return dict_store_content


# input photo page url
# output the store photo urls list
def crawl_page_photo(cate_all_shop_link_unique):

#     for each_url in cate_all_shop_link_unique:   # if input is list

	each_url = cate_all_shop_link_unique

	store_html=requests.get(each_url)
	time.sleep(3)
	store_bf=BeautifulSoup(store_html.text,"html.parser")
	try:
		store_photo_page_url = 'http://www.ipeen.com.tw'+ [tag['href'] for tag in store_bf.find_all("a", {"href":re.compile("photos")})][0]

		store_photo_url = store_photo_page_url
		store_photo_html=requests.get(store_photo_url)
		time.sleep(3)
		store_photo_bf=BeautifulSoup(store_photo_html.text,"html.parser")
		photo_urls = [tag['href'] for tag in store_photo_bf.find_all("a", {"data-label":"分享文照片"})]
		photo_urls2 = [tag['href'] for tag in store_photo_bf.find_all("a", {"data-label":"即時愛評照片"})]

		photo_urls.extend(photo_urls2)

		return photo_urls
	except:
		return []

if __name__ =='__main__':

	url="http://www.ipeen.com.tw/tainan/channel/F"
	response=requests.get(url)
	Soup=BeautifulSoup(response.text,"html.parser")
	texts = Soup.find_all('a',class_='a37 ga_tracking')

	food_cate_url=[] #category
	food_cate_string=[]
	for option in texts:
		if(option['href'][:14]=="/search/tainan"):
	        # print(option.text)
			if(option.text  in  big_cate):
				food_cate_url.append(source_url+option['href'])
				food_cate_string.append(option.text)
#	print("food_cate_len:",len(food_cate_string))    # small cate number
#	print("food_cate_string",food_cate_string)       # small cate chinese


	for order, cate in enumerate(food_cate_url):
		print("cate_chinese:",food_cate_string[order])#enter find each cate
	#	print("cate:",cate)
		cate_html=requests.get(cate)
		time.sleep(3)
		cate_bf=BeautifulSoup(cate_html.text,"html.parser")

		try:
			next_page=cate_bf.find('label',class_="next_p_s").find('a',class_="ga_tracking")
			this_cate_final_page=next_page['href']
			this_cate_final_page_number = re.findall("(=[0-9]+[0-9]*[0-9]*)", this_cate_final_page)[0][1:]

			want_togo_cate_page=[]
			for i in range(1,int(this_cate_final_page_number)):
				want_togo_cate_page.append(cate+"?p="+str(i))
		except:
			print('這個類別只有一頁')
			want_togo_cate_page=[cate]

		#print("small_cate_url:",want_togo_cate_page)
		cate_all_shop_link, kind = want_to_get_shoplink(want_togo_cate_page,food_cate_string[order])
		cate_all_shop_link_unique = pd.Series(cate_all_shop_link).unique().tolist()

		cate_json=[]
		for shop_url in cate_all_shop_link_unique:
			try:
				store_content = crowl_store_content(shop_url)
			except:
				continue
		#	print(store_content['商家名稱'])
			cate_json.append(store_content)
			#print(cate_json)
			#print("shop:",shop_url)

			the_store_photo_list= crawl_page_photo(shop_url)
			for i,j in enumerate(the_store_photo_list):
				#print("photo:",i)
				#print("photourl:",j)
				file_path1=photo_peak_folder+food_cate_string[order]
				if not os.path.exists(file_path1):
					#print("no path")
					os.mkdir(file_path1)
				file_path2=photo_peak_folder+food_cate_string[order]+"/"+store_content['商家名稱']
				if not os.path.exists(file_path2):
					try:
						os.mkdir(file_path2)
					except:
						continue
				print(file_path2)
				try:
					urlretrieve(j, file_path2+"/"+str(i) + ".jpg")
				except:
					continue
		with open(json_folder+food_cate_string[order]+'.json',"w",encoding='utf-8') as outfile:
			json.dump(cate_json,outfile,ensure_ascii=False)
