import telepot
import urllib.request
from time import sleep
from bs4 import BeautifulSoup

BOT_TOKEN = '***REMOVED***'
bot = telepot.Bot(BOT_TOKEN)

def update():
	index = open("archive.html", "w")
	responses = iter(bot.getUpdates())

	for resp in responses:
		message_type = resp['message']['entities'][0]['type']
		message_id = resp['message']['message_id']

		if message_type == 'url':
			message_url = resp['message']['text']
			response = urllib.request.urlopen(message_url)
			data = response.read()
			soup = BeautifulSoup(data, "lxml")
			message_title = soup.title.string

			print(message_id, message_url, message_title)
			value = '<a href="{0}" target="_blank">{1}</a><br>'.format(message_url, message_title)
			index.write(str(value))
	index.close()

if __name__ == "__main__":
	while(1):
		print("Update")
		update()
		sleep(10)