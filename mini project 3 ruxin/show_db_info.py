from create_mongodb import connect_to_mongodb
from create_mysql import connect_to_mysql


def show_db_info(dbkind):
    if dbkind == "mysql":
        mydb = connect_to_mysql()
        sqlcursor = mydb.cursor(buffered=True)
        sqlcursor.execute("SELECT * FROM image_col")
        image_number = sqlcursor.rowcount
        print(str(image_number)+" images in the image_col Table."+"\n")    
        user_uni = set()
        sqlcursor.execute("SELECT twitter_user FROM image_col")

        results = sqlcursor.fetchall()

        for result in results:
            user_uni.add(result)

        for user_name in user_uni:
            sqlcursor.execute("SELECT * FROM image_col WHERE twitter_user= '"+user_name[0]+"'")
            image_number_user = sqlcursor.rowcount
            print(str(image_number_user)+" images in the image_col Table"+" from "+user_name[0]+".\n")  

        sqlcursor.execute("SELECT description FROM tag_col")
        tag_number = sqlcursor.rowcount
        print(str(tag_number)+" tags in the tag_col Table."+"\n")        
        max_frequent_tag = {}
        tags=sqlcursor.fetchall()

        for tag in tags:
            max_frequent_tag[tag[0]] = max_frequent_tag.get(tag[0], 0) + 1
        tags_sorted=sorted(max_frequent_tag.items(), key=lambda x: x[1], reverse=True)
        print("The most frequent tag is: " + tags_sorted[0][0]+". It is on "+str(tags_sorted[0][1])+" images.")

        mydb.commit()
        mydb.close()


    #Implement with MongoDB      
    elif dbkind == "mongodb":
        mydb = connect_to_mongodb()
        image_col = mydb["image_col"]
        tag_col = mydb["tag_col"]
        results = image_col.find()
        image_number = results.count()
        print(str(image_number)+" images in the image_col Table."+"\n")    

        user_uni = set()
        results = image_col.find()

        for result in results:
            user_uni.add(result['twitter_user'])
        #print(user_uni)
        for user_name in user_uni:
            imagequery = { "twitter_user": user_name}
            results = image_col.find(imagequery)
            length =  results.count(True)
            print(str(length)+" images in the image_col Table"+" from "+user_name+".\n") 
        ### For tags_data Table:
        #### 1. Number of all tags
        results = tag_col.find()
        tag_number = results.count(True)
        print(str(tag_number)+" tags in the tag_col Table."+"\n")    

        #### 2. The most frequent tags

        max_frequent_tag = {}

        for result in results:
            max_frequent_tag[result['description']] = max_frequent_tag.get(result['description'], 0) + 1
        #print(max_frequent_tag)
        tags_sorted=sorted(max_frequent_tag.items(), key=lambda x: x[1], reverse=True)
        print("The most frequent tag is: " + tags_sorted[0][0])


    else:
        print("Unknown databse.")
        return