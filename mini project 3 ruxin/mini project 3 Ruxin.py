# Copyright 2018 Ruxin Diao ruxin@bu.edu
import io
import mysql.connector
import pymongo
import pprint
import wget
import tweepy
import os
import shutil
from create_mongodb import connect_to_mongodb
from create_mysql import connect_to_mysql
from to_video import to_video
from search_api import search_api
from show_db_info import show_db_info


def google_vision_label(dbkind):
    # load google credentials.json to os environment
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/bianfuru/Desktop/601/project1/miniproject1-b5af4e44e5d9.json"
    # Imports the Google Cloud client library
    from google.cloud import vision
    from google.cloud.vision import types
    import PIL.Image as Image
    import PIL.ImageDraw as ImageDraw
    import PIL.ImageFont as ImageFont

    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # I have created a new file named"pictures" in the working directory fot the annotated pictures
    path = "pictures"
    imgs = os.listdir(path)
    cnt = 1
    for img in imgs:
        file_name = os.path.join(path, img)

        # Loads the image into memory
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()

        image = types.Image(content=content)

        # Performs label detection on the image file
        response = client.label_detection(image=image)
        labels = response.label_annotations

        descriptions = []
        for label in labels:
            descriptions.append(label.description)
        # sep = "\n", change line for every label
        string = "\n".join(descriptions)

        if dbkind == "mysql":
            mydb = connect_to_mysql()
            sqlcursor = mydb.cursor(buffered=True)
            sqlcursor.execute("SELECT img_id FROM image_col WHERE image_name = '" + img + "'")
            results = sqlcursor.fetchall()
            image_ids = []

            for result in results:
                # print("\n"+result)
                image_ids.append(int(result[0]))
            image_ids.sort()
            # print(image_ids)
            if len(image_ids) > 0:
                img_id = str(image_ids[-1])
                sqlcursor.execute("SELECT * FROM tag_col")
                t_id = sqlcursor.rowcount
                if t_id < 0:
                    t_id = 0
                for tag in descriptions:
                    t_id = t_id + 1
                    ta_id = str(t_id)
                    sqlcursor.execute("INSERT INTO tag_col (tag_id, description, img_id) VALUES (%s, %s, %s)",
                                     (ta_id, tag, img_id))
                mydb.commit()
                mydb.close()
            else:
                continue



        # Implement with MongoDB
        elif dbkind == "mongodb":
            mydb = connect_to_mongodb()
            image_col = mydb["image_col"]
            tag_col = mydb["tag_col"]
            myres = image_col.find({"image_name": img})
            max_id = 0
            for res in myres:
                if res['_id'] > max_id:
                    max_id = res['_id']
            img_id = max_id
            results = tag_col.find()
            t_id = results.count()
            for tag in descriptions:
                t_id = t_id + 1
                tag_col.insert_one({"_id": t_id, "description": tag, "img_id": img_id})

        else:
            print("Unknown databse.")
            return

        # Using pillow module
        FONT_PATH = "/Aplications/Microsoft Excel.app/Contents/Resources/Fonts/Times.ttf"
        font = ImageFont.truetype('Times.ttf', 50)

        # define position to start drawing text
        (x, y) = (0, 0)
        im = Image.open(file_name).convert('RGB')
        draw = ImageDraw.Draw(im)
        # draw string text on the img, with rgb color (255,255,0,0)
        draw.text((x, y), string, (255, 0, 0, 0), font=font)
        im.save('pictures/' + str('%d' % cnt) + '.jpg', 'JPEG')
        cnt += 1


def get_all_tweets(screen_name, dbkind):
    consumer_key = "Enter your consumer_key"
    consumer_secret = "Enter your consumer_secret"
    access_key = "Enter your access_key"
    access_secret = "Enter your access_secret"

    # Twitter only allows access to a users most recent 3240 tweets with this method
    screen_name = "@" + screen_name
    print("\n" + screen_name)
    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    # initialize a list to hold all the tweepy Tweets
    alltweets = []
    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=10)
    # save most recent tweets
    alltweets.extend(new_tweets)
    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=10, max_id=oldest)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        if (len(alltweets) > 15):
            break

    # save the pictures as a list
    picture_list = []
    for tweet in alltweets:
        tem = tweet.entities.get('media', [])
        if (len(tem) > 0):
            picture_list.append(tem[0]['media_url'])
    # download the pictures into the folder that I have created
    path = "pictures"

    # Implement with MySQL
    if dbkind == "mysql":
        mydb = connect_to_mysql()
        sqlcursor = mydb.cursor(buffered=True)
        sqlcursor.execute("SELECT * FROM image_col")
        img_id = sqlcursor.rowcount
        if img_id < 0:
            img_id = 0

        images_file = {}
        for picture in picture_list:
            wget.download(picture, out=path)
            for file in os.listdir(path):
                if file not in images_file:
                    im = file
                    images_file[file] = 1
            img_id = img_id + 1
            sqlcursor.execute("INSERT INTO image_col (img_id, twitter_user, image_name) VALUES (%s, %s, %s)",
                             (str(img_id), screen_name, im))
        mydb.commit()
        mydb.close()


    # Implement with MongoDB
    elif dbkind == "mongodb":
        mydb = connect_to_mongodb()
        image_col = mydb["image_col"]
        results = image_col.find()
        img_id = results.count()
        images_file = {}
        for picture in picture_list:
            wget.download(picture, out=path)
            for file in os.listdir("pictures"):
                if file not in images_file:
                    im = file
                    images_file[file] = 1
            img_id = img_id + 1
            img_dict = {"_id": img_id, "twitter_user": screen_name, "image_name": im}
            image_col.insert_one(img_dict)
    else:
        print("Unknown databse.")
        return



'''-------------------------main program-------------------------- '''
dbkind = input("Please select which database you want to use? mysql/mongodb  ")

for file in os.listdir("pictures"):
    os.remove("pictures/" + file)
if "twittervideo.mp4" in os.listdir():
    os.remove("twittervideo.mp4")
if dbkind == "mongodb" or dbkind == "mysql":
    screen_name = input("screen_name: @")
    try:
        get_all_tweets(screen_name, dbkind)
        print("\n" + "Tweets downloaded.")
    except:
        print("User Not Found.")
    google_vision_label(dbkind)
    print("\n" + "Labels detected.")
    to_video()
    os.system("twittervideo.mp4")
    search = input("Do you want to do a search? y/n ")
    if search == "y":
        search_api(dbkind)
    show_db = input("Do you want to show database info? y/n ")
    if show_db == "y":
        show_db_info(dbkind)
else:
    print("\n" + "Unknown database.")
