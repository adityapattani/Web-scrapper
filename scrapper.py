import csv
import bs4
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as urlReq
import re
import threading
import os

pagesScrapped = 0

def scrapper(urlToRequest, firstPage, lastPage, fileName, openMode, newlineDelimiter):
	global pagesScrapped
	#Opening a csv file to write data in it
	with open(fileName, openMode, newline=newlineDelimiter) as csv_file:
		writer = csv.writer(csv_file)

		#For all pages in starting from the first to the last page
		for page in range(firstPage,lastPage):
			uClient = urlReq(urlToRequest + "page/" + str(page))
			page_html = uClient.read()
			uClient.close()

			#Initializing the page soup to scrape data
			page_soup = soup(page_html, "html.parser")
			containers = page_soup.findAll("h2", {"class":"title"})
		
			#Showing the progress as well as opening a separate page for a game to get RAM as well as Size
			for container in containers:
				pagesScrapped += 1
				print("\rScrapped pages: " + str(pagesScrapped), end='')
				uClientGamePage = urlReq(urlToRequest + "-".join(container.a.text.split(" ")).lower().replace("'","").replace('"','').replace("’",""))
				game_page_html = uClientGamePage.read()
				uClientGamePage.close()

				#All data that is to be scrapped
				try:
					game_page_soup = soup(game_page_html, "html.parser")
					ramReq = game_page_soup.find(text=re.compile("^RAM"))
					setupSize = game_page_soup.find(text=re.compile("^Setup Size"))
					cpuReq = game_page_soup.find(text=re.compile("^CPU"))
					OSReq = game_page_soup.find(text=re.compile("^Operating System"))
					genres = game_page_soup.findAll("li", {"class":"active-parent"})

					genre_string = ""
					for genre in genres:
						genre_string += genre.a.text + " "
					
					if setupSize is None:
						setupSize = "Setup Size: NA"
					if ramReq is None:
						ramReq = "RAM: NA"

					writer.writerow([" ".join(container.a.text.split(" ")[:-2]), ramReq.split(":")[1], setupSize.split(":")[1], cpuReq.split(":")[1], OSReq.split(":")[1], genre_string])
				except AttributeError:
					print("\nValue error in game: " + " ".join(container.a.text.split(" ")[:-2]))

#All the variables to make the scrapping dynamic
firstPage = 1
lastPage = 300
urlToRequest = 'http://www.oceanofgames.com/'
fileName = "games"
openMode = "a"
newlineDelimiter = ""

print("Scrapper Initialized. Beginning scrapping")

tuple1 = (urlToRequest, firstPage, lastPage//4, fileName + "1", openMode, newlineDelimiter)
tuple2 = (urlToRequest, lastPage//4, lastPage//2, fileName + "2", openMode, newlineDelimiter)
tuple3 = (urlToRequest, lastPage//2, (lastPage*3)//4, fileName + "3", openMode, newlineDelimiter)
tuple4 = (urlToRequest, (lastPage*3)//4, lastPage, fileName + "4", openMode, newlineDelimiter)

t1 = threading.Thread(target = scrapper, args = tuple1)
t2 = threading.Thread(target = scrapper, args = tuple2)
t3 = threading.Thread(target = scrapper, args = tuple3)
t4 = threading.Thread(target = scrapper, args = tuple4)

t1.start()
t2.start()
t3.start()
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()

finalData = ""
for i in range(4):
	with open(fileName + str(i+1), 'r') as myfile:
		finalData += myfile.read()

	os.remove(fileName + str(i+1))

with open("games.csv", 'a') as myfile:
	myfile.write("Title, RAM required, Game size, Minimum CPU, Minimum OS, Genres\n")
	myfile.write(finalData)

print("\n\nAll pages scrapped!")