from bs4 import BeautifulSoup
from subprocess import Popen
from urllib import request
import re
import requests
import clipboard
import os

BASE_URL = "https://archive.nothingburger.today/"
HOME_PATH = os.path.expanduser("~")
DOWNLOAD_PATH = HOME_PATH + '/nothingburger/'
FOLDERS = DOWNLOAD_PATH + 'nothingburger-folders.txt'
FILES = DOWNLOAD_PATH + 'nothingburger-files.txt'
image_links = []
files = {
		'png', 'jpg', 'pdf', 'video', 'mp4', 'mp3', 'gif', 'jpeg', 'image',
		'zip', 'text', 'rar', 'doc', 'lit', 'rtf', 'audio', 'html', 'torrent'
	}

def getSoup(input_url):
	response = requests.get(input_url, verify=False)
	data = response.text
	soup = BeautifulSoup(data, 'html.parser')
	return soup

def getMainFolders(user_url):
	a = []
	l = 0
	soup = getSoup(user_url)
	link_attrs = soup.find_all('tr')
	for cl in link_attrs[1:]:
		for td in soup.find_all('td', class_='indexcolname'):
			a.append(td.text)
	a = a[:8]
	return a

def getUrlList(root_folders):
	link_list = []
	for l in root_folders:
		new_url = BASE_URL + l
		link_list.extend([new_url])
	return link_list

def iterThroughLinks(links):
	for link in links:
		soup = getSoup(link)
		return (checkFileType(link, soup))


def checkFileType(base_link, folder_soup):
	'''
		Gets soup and checks img tags for file type.
	Extracts text inside braces with regex r"\[(\w+)\]"
	and compares text to set "files" to determine type
	Once filetype is acquired, it calls separate
	methods for processing each type.
		'''

	f = 0
	link_attrs = folder_soup.find_all('tr')

	for l in link_attrs[2:]:
		link_attrs_filetype = l.find('img')
		get_type = link_attrs_filetype['alt']
		if get_type == '[   ]':
			get_type = '[rar]'
		n = re.search(r"\[(\w+)\]", get_type)
		type = n.group(1)
		link_attrs_get_name = l.find('td', class_='indexcolname')
		name = link_attrs_get_name.text

		if type not in files:
			folder_link = base_link + name
			with open(FOLDERS, "a") as f:
				f.write(folder_link + '\n')
			isSubFolder(name, folder_link)
		else:
			image_link = base_link + name
			image_links.extend([image_link])
			with open(FILES, "a") as f:
				f.write(image_link + '\n')
	return image_links



def isSubFolder(folder, goto_link):
	if(folder != "Parent Directory"):
		checkFileType(goto_link, getSoup(goto_link))
	else:
		pass

def createFolders():
	with open(FOLDERS, "r") as f:
		data = f.readlines()
		for folder in data:
			n = re.search(r"[^https://archive.nothingburger.today](.+)", folder)
			type = n.group(0)
			os.makedirs(HOME_PATH + "/nothingburger/" + type)

def makeFiles():
	with open(FILES, "r") as f:
		data = f.readlines()
		for file in data:
			filepath = HOME_PATH + "/nothingburger/" + type
			f = open(filepath, "w")

def downloadFile(link):
	userAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
	accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
	acceptCharset = 'ISO-8859-1,utf-8;q=0.7,*,q=0.3'
	acceptLang = 'en-US,en;q=0.8'
	connection = 'keep-alive'

	headers = {
		'User-Agent': userAgent,
		'Accept': accept,
		'Accept-Charset': acceptCharset,
		'Accept-Language': acceptLang,
		'Connection': connection,
	}

	n = re.search(r"[^https://archive.nothingburger.today](.+)", link)
	filename = n.group(0)
	print('Downloading...')
	path = DOWNLOAD_PATH + filename
	r = requests.get(link, allow_redirects=True, verify=False)
	open(path , 'wb').write(r.content)
	print('File downloaded to {}'.format(os.path.abspath(path)))

def main():
	os.makedirs(DOWNLOAD_PATH, exist_ok=True)
	if(os.path.exists(FILES) and os.path.exists(FOLDERS)):
		createFolders()
		with open(FILES, "r") as f:
			data = f.readlines()
			for file in data:
				downloadFile(file)
	else:
		image_links = iterThroughLinks(getUrlList(getMainFolders(BASE_URL)))
		print(image_links)
		createFolders()
		for image_link in image_links:
			downloadFile(image_link)

if __name__ == "__main__":
	main()
