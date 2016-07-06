import telepot
import urllib.request
import json
import jinja2
import time

from bs4 import BeautifulSoup
from pymongo import MongoClient

BOT_TOKEN = ''
MONGODB_NAME = ''

def UpdateFromTelegram():
    responses = iter(bot.getUpdates())

    for resp in responses:
        message = resp['message']
        if 'entities' not in message:
            continue

        message_type = message['entities'][0]['type']
        message_id = message['message_id']

        if message_type == 'url':
            if FindRecord(message_id) == False:
                message_url = resp['message']['text']
                response = urllib.request.urlopen(message_url)
                data = response.read()
                soup = BeautifulSoup(data, "lxml")
                message_title = soup.title.string

                print(message_id, message_url, message_title)
                InsertDB(message_id, message_url, message_title)
            else:
                print(time.ctime(time.time()) + " id:" + str(message_id) + " Exist!")

    UpdateHTML()

def FindRecord(message_id):
    Conn = MongoClient(MONGODB_NAME)
    database = Conn['archivebot']
    mycollection = database.entries
    res = mycollection.find({"id": message_id})
    if res.count() == 0:
        return False
    else:
        return True

def InsertDB(message_id, message_url, message_title):
    print(time.ctime(time.time()) + " Insert " + message_id + " " + message_url)
    Conn = MongoClient(MONGODB_NAME)
    database = Conn['archivebot']
    mycollection = database.entries
    post = {"id": message_id, "url": message_url, "title": message_title}
    mycollection.insert(post)

def UpdateHTML():
    print(time.ctime(time.time()) + " Update HTML")
    Conn = MongoClient(MONGODB_NAME)
    database = Conn['archivebot']
    mycollection = database.entries

    templateLoader = jinja2.FileSystemLoader( searchpath="/" )
    templateEnv = jinja2.Environment( loader=templateLoader )
    template = templateEnv.get_template("/home/clarkzjw/code/ArchiveBot/archive.jinja")

    templateMessage = []
    for i in mycollection.find():
        templateMessage.append({"url": i["url"], "title": i["title"]})

    templateR = {"messages": templateMessage}
    output = template.render(templateR)
    index = open("/home/clarkzjw/Dropbox/archive.html", "w")
    index.write(output)
    index.close()

if __name__ == "__main__":
    configfile = open("./config.json")
    config = json.load(configfile)
    MONGODB_NAME = config["MONGODB_NAME"]
    BOT_TOKEN = config["BOT_TOKEN"]

    bot = telepot.Bot(BOT_TOKEN)
    while(True):
        print(time.ctime(time.time()) + " Update from Telegram")
        UpdateFromTelegram()
        time.sleep(10)
