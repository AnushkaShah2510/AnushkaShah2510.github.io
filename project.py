from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from bs4 import BeautifulSoup
import os
import time
import requests
import pymongo
import pymysql
import warnings
import json
warnings.filterwarnings("ignore")


# Question 2: yellow pages
# converts "three half" to 3.5
def get_number_from_element_class(element_class_list):
    # example class list - [result-rating four half]
    # so we ignore the first element in the class list
    first_rating_class = element_class_list[1]
    number = 0

    if first_rating_class == 'one':
        number = 1
    elif first_rating_class == 'two':
        number = 2
    elif first_rating_class == 'three':
        number = 3
    elif first_rating_class == 'four':
        number = 4
    else:
        number = 5

    # now let's see if there is a half star added
    if len(element_class_list) > 2:
        if (element_class_list[2] == 'half'):
            number += 0.5
    
    return number


print("q2")
def q2():
	driver = webdriver.Chrome(executable_path="chromedriver", options=webdriver.ChromeOptions())
	driver.implicitly_wait(10) 
	url = 'https://opensea.io/collection/boredapeyachtclub?search[sortAscending]=false&search[stringTraits][0][name]=Fur&search[stringTraits][0][values][0]=Solid%20Gold'
	driver.get(url)
	headers = {
       'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
	for N in range(8):
		try:
		    print(N)
		    '''
		        Have to call driver.find_elements(By.CSS_SELECTOR, ".Asset--anchor") again and again in the the loop because of stale element reference exception.
		        So, the reason is that as the DOM reloads as we visit ape pages and come back and so the old element references collected earlier become stale.
		        So, the code kept crashing if I had the statement outside the loop
		    '''
		    expapes = driver.find_elements(By.CSS_SELECTOR, ".Asset--anchor") 
		    expensive_ape = expapes[N]
		    expensive_ape.click()
		    time.sleep(2)
		    
		    current_url = driver.current_url
		    id_begin_index = current_url.rindex('/')
		    ape_id = current_url[id_begin_index + 1:]
		    filename = f"bayc_{ape_id}.html"

		    with open(filename, "w") as file:
		        file.write(driver.page_source)

		    driver.back() 
		    time.sleep(4)

		# needed to scroll down if element not clickable
		except ElementClickInterceptedException:
			driver.execute_script("window.scrollBy(0,200)")
			N -= 1 # need to process this listing again

		except Exception as e:
			print(e)
			print('Deal with exception')

	driver.quit()


'''
return a list of all the records from the parsed html files
'''
print("q3")
def q3():
	DBHOST = 'localhost'
	DBUSER = 'root'
	DBPASS = 'Hetvi1004.'
	DBPORT = 3306

	db = pymysql.connect(host = DBHOST, user = DBUSER, password = DBPASS, port = DBPORT)
	client = pymongo.MongoClient('mongodb://localhost:27017/')
	db = client['db_individualproject']
	collection = db['bayc']
	print(db.list_collection_names())

	data = []
	directory = './'
	for root, dirnames, filenames in os.walk(directory):
		for filename in filenames:
			if filename.endswith('.html') and 'bayc' in filename:
				try:
					with open(filename, 'r') as fr:
						print('*********Processing ' + filename + '***********')
						filename_dot_index = filename.index('.')
						ape_id = filename[5: filename_dot_index]
						soup = BeautifulSoup(fr, 'html.parser')
						attribute_elements = soup.find('div', {'class': 'Panel--isContentPadded item--properties'})
						for attribute_element in attribute_elements:
						        property_types = attribute_element.find_all('div', {'class': 'Property--type'})
						        property_values = attribute_element.find_all('div', {'class': 'Property--value'})
						        property_rarities = attribute_element.find_all('div', {'class': 'Property--rarity'})

						        ape_data = {
						        	'ape_name': ape_id,
						        	'attributes': []
						        }

						        for i in range(len(property_types)):
						        	attribute = {
						        		property_types[i].text: {
						        			'value': property_values[i].text,
						        			'rarity': property_rarities[i].text
						        		}
						        	}
						        	ape_data['attributes'].append(attribute)

						data.append(ape_data)

				except Exception as e:
					print(e)
					print('File could not be processed')

		collection.insert_many(data)
		db.close()


# '''
# Question 1: Bored apes
# Add pseudocode
# '''
# def q2():
# 	# q2_download_html_files()
# 	q3()


def q4():
	url = 'https://www.yellowpages.com/search?'
	headers = {
	    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
	    'HTTP_CONNECTION':"keep-alive",
	    'HTTP_ACCEPT':'*/*',
	    'HTTP_ACCEPT_ENCODING':'gzip, deflate'
	}

	# connect to BeautifulSoup library : params got from inspect > input > name = ''
	page = requests.get(url, headers = headers,
	                    params = {'search_terms': 'Pizzeria', 'geo_location_terms': 'San Francisco'})
	soup = BeautifulSoup(page.content, 'html.parser')

	with open('sf_pizzeria_search_page.htm', 'w') as f:
	    f.write(page.content.decode('utf-8'))

def q5():
	# q4() # because question 5 needs the downloaded file from question 4. Can comment if already ran q4()

	with open('sf_pizzeria_search_page.htm', 'r') as f:
	    page = f.read()

	organic_listing_div = soup.find('div', {'class': 'organic'})
	organic_listings = organic_listing_div.find_all('div', {'class': 'result'})



	# loop through the listings and extract the desired information
	for i, listing in enumerate(organic_listings):
	    rank = i + 1  # search rank is just the index plus 1
	    name = listing.find('a', {'class': 'business-name'}).text.strip()
	    print(rank , ".", name)
	    url = listing.find('a', {'class': 'business-name'}) if listing.find('a', {'class': 'business-name'}) else ''
	    if url:
	        url = url = 'https://www.yellowpages.com' + url.get('href')
	    else:
	        url = ''
	    
	    print('Website URL:', url)
	    # rating 
	    rating = ''
	    rating_count = ''
	    rating = listing.find('div', {'class': 'result-rating'}) if listing.find('div', {'class': 'result-rating'}) else ''
	    
	    if rating != '':
	        rating = get_number_from_element_class(rating['class'])
	    print('Rating:', rating)
	    # rating count
	    rating_count = listing.find('span', {'class': 'count'}) if listing.find('span', {'class': 'count'}) else ''
	    if rating_count:
	        rating_count = rating_count.get_text(strip=True)
	    else:
	        rating_count=''
	    print('Number of Reviews:', rating_count)

	    # TA rating + count
	    tripadvisor_rating = ''
	    tripadvisor_rating_count = ''
	    
	    tripadvisor_div = listing.find('div', {'class': 'ratings'}) if listing.find('div', {'class': 'ratings'}) else ''
	    
	    if tripadvisor_div != '' and tripadvisor_div.get("data-tripadvisor") is not None:
	        tripadvisor_data = json.loads(tripadvisor_div.get("data-tripadvisor"))
	        tripadvisor_rating = tripadvisor_data['rating']
	        tripadvisor_rating_count = tripadvisor_data['count']
	    
	    print('Trip Advisor Rating:', tripadvisor_rating)
	    print('Number of Trip Advisor Rating:', tripadvisor_rating_count)

	    # address, phone and price range
	    listing_info = listing.find('div', {'class': 'info-section info-secondary'}) 
	    phone = listing_info.find('div', {'class': 'phones phone primary'}) if listing_info.find('div', {'class': 'phones phone primary'}) else ''
	    print("Phone Number:", phone.string)

	    address_div = listing.find('div', {'class': 'adr'})
	    street_address = address_div.find('div', {'class': 'street-address'}).text.strip()
	    locality = address_div.find('div', {'class': 'locality'}).text.strip()
	    address = street_address + ', ' + locality
	    print("Address:", address)

	    price_range = listing_info.find('div', {'class': 'price-range'}) if listing_info.find('div', {'class': 'price-range'}) else ''
	    print("Price Range:", price_range.string) if price_range != '' else print("Price Range:", price_range)

	    # Years in Bus
	    years_in_business = listing.find('div', {'class': 'years-in-business'}).text.strip() if listing.find('div', {'class': 'years-in-business'}) else ''
	    print('Years in Business:', years_in_business)

	    #Review
	    review = listing.find('div', {'class': 'snippet'}).text.strip() if listing.find('div', {'class': 'snippet'}) else ' '
	    print("Review:", review)

	    #Amenities
	    # amenities = listing.find('span', {'class': 'amenities-icon'})['xlink:href'] if listing.find('span', {'class': 'amenities-icon'})['xlink:href'] else 'NA'
	    amenities_list = [ ]
	    amenities_icons = listing.find('span', {'class': 'amenities-icons'})
	    if amenities_icons:
	        amenities = amenities_icons.find_all('svg', {'class': 'amenities-icon'})
	        for amenity in amenities:
	            amenity_name = amenity.find('use').get('xlink:href').split('-')[-1]
	            amenities_list.append(amenity_name)
	    else:
	        amenities_list.append('')
	    print("Amenities:", amenities_list)


def q6():
	DBHOST = 'localhost'
	DBUSER = 'root'
	DBPASS = 'Hetvi1004.' #enter password here
	DBPORT = 3306

	db = pymysql.connect(host = DBHOST, user = DBUSER, password = DBPASS, port = DBPORT)
	client = pymongo.MongoClient("mongodb://localhost:27017/")
	db = client["db_individualproject"]

	collection = db["sf_pizzerias"]

	print(db.list_collection_names())
	with open('sf_pizzeria_search_page.htm', 'r') as f:
	    page = f.read()

	soup = BeautifulSoup(page, 'html.parser')


	organic_listing_div = soup.find('div', {'class': 'organic'})
	organic_listings = organic_listing_div.find_all('div', {'class': 'result'})

	mongo_docs = []
	# loop through the listings and extract the desired information
	for i, listing in enumerate(organic_listings):
	    rank = i + 1  # search rank is just the index plus 1
	    name = listing.find('a', {'class': 'business-name'}).text.strip()
	    print(rank , ".", name)
	    url = listing.find('a', {'class': 'business-name'}) if listing.find('a', {'class': 'business-name'}) else ''
	    if url:
	        url = 'https://www.yellowpages.com' + url.get('href')
	    else:
	        url = ''
	    
	    # rating 
	    rating = ''
	    rating_count = ''
	    rating = listing.find('div', {'class': 'result-rating'}) if listing.find('div', {'class': 'result-rating'}) else ''
	    
	    if rating != '':
	        rating = get_number_from_element_class(rating['class'])

	    # rating count
	    rating_count = listing.find('span', {'class': 'count'}) if listing.find('span', {'class': 'count'}) else ''
	    if rating_count:
	        rating_count = rating_count.get_text(strip=True)
	    else:
	        rating_count=''


	    # TA rating + count
	    tripadvisor_rating = ''
	    tripadvisor_rating_count = ''
	    
	    tripadvisor_div = listing.find('div', {'class': 'ratings'}) if listing.find('div', {'class': 'ratings'}) else ''
	    
	    if tripadvisor_div != '' and tripadvisor_div.get("data-tripadvisor") is not None:
	        tripadvisor_data = json.loads(tripadvisor_div.get("data-tripadvisor"))
	        tripadvisor_rating = tripadvisor_data['rating']
	        tripadvisor_rating_count = tripadvisor_data['count']
	    


	    # address, phone and price range
	    listing_info = listing.find('div', {'class': 'info-section info-secondary'}) 
	    phone = listing_info.find('div', {'class': 'phones phone primary'}) if listing_info.find('div', {'class': 'phones phone primary'}) else ''


	    address_div = listing.find('div', {'class': 'adr'})
	    street_address = address_div.find('div', {'class': 'street-address'}).text.strip()
	    locality = address_div.find('div', {'class': 'locality'}).text.strip()
	    address = street_address + ', ' + locality


	    price_range = listing_info.find('div', {'class': 'price-range'}) if listing_info.find('div', {'class': 'price-range'}) else ''


	    # Years in Bus
	    years_in_business = listing.find('div', {'class': 'years-in-business'}).text.strip() if listing.find('div', {'class': 'years-in-business'}) else ''


	    #Review
	    review = listing.find('div', {'class': 'snippet'}).text.strip() if listing.find('div', {'class': 'snippet'}) else ' '


	    #Amenities
	    # amenities = listing.find('span', {'class': 'amenities-icon'})['xlink:href'] if listing.find('span', {'class': 'amenities-icon'})['xlink:href'] else 'NA'
	    amenities_list = [ ]
	    amenities_icons = listing.find('span', {'class': 'amenities-icons'})
	    if amenities_icons:
	        amenities = amenities_icons.find_all('svg', {'class': 'amenities-icon'})
	        for amenity in amenities:
	            amenity_name = amenity.find('use').get('xlink:href').split('-')[-1]
	            amenities_list.append(amenity_name)
	    else:
	        amenities_list.append('')

	    pizzeria_dict = {
			'rank': rank,
			'name': name,
			'url': url,
			'rating': rating,
			'rating_count': rating_count,
			'tripadvisor_rating': tripadvisor_rating,
			'tripadvisor_rating_count': tripadvisor_rating_count,
			'phone': phone.string,
			'address': address,
			'price_range': price_range.string if price_range != '' else None,
			'years_in_business': years_in_business,
			'review': review,
			'amenities': amenities_list
		}

	    mongo_docs += [pizzeria_dict]


	collection.insert_many(mongo_docs)

	collist = db.list_collection_names()

	# just debug code
	if "sf_pizzerias" in collist:
			print("The collection exists.")


def q7():
	DBHOST = 'localhost'
	DBUSER = 'root'
	DBPASS = 'Hetvi1004.' #enter password here
	DBPORT = 3306

	db = pymysql.connect(host = DBHOST, user = DBUSER, password = DBPASS, port = DBPORT)
	client = pymongo.MongoClient("mongodb://localhost:27017/")
	db = client["db_individualproject"]
	collection = db["sf_pizzerias"]

	for docu in collection.find():
	    url = docu['url']
	    sr = docu['rank']
	    page = requests.get(url).text
	    with open(f'sf_pizzerias_{sr}.htm', 'w') as file:
	        file.write(page)

def q8():
	# q7() # because question 8 needs the downloaded file from question 7. Can comment if already ran q7()

	DBHOST = 'localhost'
	DBUSER = 'root'
	DBPASS = 'Hetvi1004.' #enter password here
	DBPORT = 3306

	db = pymysql.connect(host = DBHOST, user = DBUSER, password = DBPASS, port = DBPORT)
	client = pymongo.MongoClient("mongodb://localhost:27017/")
	db = client["db_individualproject"]
	collection = db["sf_pizzerias"]

	for docu in collection.find():
	    url = docu['url']
	    sr = docu['rank']
	    page = requests.get(url).text
	    
	    with open(f'sf_pizzerias_{sr}.htm', 'r') as fread:
	        soup = BeautifulSoup(fread, 'html.parser')
	        
	    website = soup.find('a', {'class': 'website-link dockable'}).get('href') if soup.find('a', {'class': 'website-link dockable'}) else ' ' 

	    print("Website:", website)
	    address = soup.find('span', {'class': 'address'}).text
	    print("Address:", address)
	    phone_num1 = soup.find('a', {'class': 'phone dockable'})
	    phone_num = phone_num1.get('href')
	    print("Phone Number:", phone_num)
	    
	    print('*************\n')


def q9():
	DBHOST = 'localhost'
	DBUSER = 'root'
	DBPASS = 'Hetvi1004.' #enter password here
	DBPORT = 3306

	db = pymysql.connect(host = DBHOST, user = DBUSER, password = DBPASS, port = DBPORT)
	client = pymongo.MongoClient("mongodb://localhost:27017/")
	db = client["db_individualproject"]
	collection = db["sf_pizzerias"]

	i = 1

	for docu in collection.find():
	    url = docu['url']
	    i += 1
	    sr = docu['rank']
	    page = requests.get(url).text
	    
	    with open(f'sf_pizzerias_{sr}.htm', 'r') as fread:
	        soup = BeautifulSoup(fread, 'html.parser')
	        
	    website = soup.find('a', {'class': 'website-link dockable'}).get('href') if soup.find('a', {'class': 'website-link dockable'}) else ' ' 

	    print("Website:", website)
	    # address = soup.find('span', {'class': 'address'}).text

	    address_section = soup.find("section", {"id": "details-card"})
	    address = address_section.find_all('p')[1].text



	    print("Address:", address[9:])
	    phone_num1 = soup.find('a', {'class': 'phone dockable'})
	    phone_num = phone_num1.get('href')
	    print("Phone Number:", phone_num)
	    api_access_key = '42bef5cfc42aa7cc37408ec3ee63fe0f'
	    post_url = f'http://api.positionstack.com/v1/forward?access_key={api_access_key}&query={address}'

	    # headers = {
		#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
		# }

	    response = requests.get(post_url)
	    data = json.loads(response.text)
	    print(data)

	    if len(data['data']) > 0:
	    	latitude = data['data'][0]['latitude']
	    	longitude = data['data'][0]['longitude']
	    else:
	    	latitude = ''
	    	longitude = ''

	    my = collection.update_one(
            	{"address": address[9:]},
            	{"$set": {
                	'phone_num': phone_num,
                	'website': website,
                	'latitude': latitude,
                	'longitude': longitude
            	}}
        	)

	    print(my.modified_count, f'for {address} updated in document')

	    if i > 30:
	    	break





if __name__ == '__main__':
	try:
		# q2()
		# q3()
		# q4() # downloads the top 30 pizzeria yellow pages html file
		# q6() # extract information from the downloaded file and save it in mongo db
		# q7() # download each of the 30 pizzeria's website
		q8()
		q9() # update the phone, website, and geolocation
	except Exception as e:
		print(e)
		print('exception')