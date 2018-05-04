from flickrapi import FlickrAPI
import os, json
from pathlib import Path

FLICKR_PUBLIC = '9532e8b9dfaee5884e6ab6c1c3d15d83'
FLICKR_SECRET = json.load(open(str(Path(os.getcwd())/"config.txt"), "r"))["flickrapi_secret"]
flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')

import requests, os
from pathlib import Path

root_path = os.getcwd()

queries = ["pen", "book"]

extras='url_m,url_z,url_c,url_l,url_o'
url_lookup = ['url_'+letter for letter in "ocmzl"]

from pprint import *

for query in queries:

	photos_json = flickr.photos.search(text=query, content_type = 1, sort = "relevance", extras=extras, per_page=500, page = 1)
	
	photos = photos_json['photos']['photo']

	photo_id = 0

	for photo in photos:
		
		for url_type in url_lookup:
			if(url_type in photo.keys()):
				img_data = requests.get(photo[url_type]).content

				directory = str(Path(root_path)/(query+"s"))
				
				if not os.path.isdir(directory):
					os.makedirs(directory)
					
				with open(str(Path(root_path)/(query+"s")/'{}_{}.jpg'.format(query,photo_id)), 'wb') as handler:
					handler.write(img_data)
				break

		photo_id += 1